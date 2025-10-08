# detdevlib/etl/db.py

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, Optional, Self

import pandas as pd
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL, Engine

from detdevlib.utils.etc import clean_dict

logger = logging.getLogger(__name__)


class DialectSettings(ABC):
    """Abstract base class for dialect-specific settings."""

    @abstractmethod
    def get_connection_url(self) -> str:
        """Constructs and returns a SQLAlchemy connection URL.

        Returns:
            str: A SQLAlchemy connection URL.
        """
        pass

    def get_procedures_sql(
        self, schema: Optional[str] = None
    ) -> Optional[tuple[str, dict]]:
        """Returns the SQL query to list stored procedures.

        Args:
            schema (Optional[str]): The schema to query.

        Returns:
            Optional[tuple[str, dict]]: A tuple with the SQL query string
                and a dictionary of parameters, or None if not supported.
        """
        return None


class MSSQLSettings(BaseSettings, DialectSettings):
    """Configuration for 'mssql' dialect."""

    model_config = SettingsConfigDict(env_prefix="MSSQL_")

    hostname: str
    database: str
    username: str
    password: SecretStr
    driver: str = "ODBC Driver 18 for SQL Server"

    def get_connection_url(self) -> str:  # noqa: D102
        return URL.create(
            "mssql+pyodbc",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.hostname,
            database=self.database,
            query={
                "driver": self.driver,
                "Encrypt": "yes",
                "TrustServerCertificate": "no",
                "ConnectionTimeout": "30",
            },
        ).render_as_string(hide_password=False)

    def get_procedures_sql(
        self, schema: Optional[str] = None
    ) -> tuple[str, dict]:  # noqa: D102
        params = {"schema": schema}
        query = f"""
            SELECT ROUTINE_NAME
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_TYPE = 'PROCEDURE'
            {"AND ROUTINE_SCHEMA = :schema" if schema is not None else ""}
            ORDER BY ROUTINE_NAME;
        """
        return query, clean_dict(params)


class PostgreSQLSettings(BaseSettings, DialectSettings):
    """Configuration for the 'postgresql' dialect."""

    model_config = SettingsConfigDict(env_prefix="PGSQL_")

    hostname: str
    database: str
    username: str
    password: SecretStr
    port: int = 5432

    def get_connection_url(self) -> str:  # noqa: D102
        return URL.create(
            "postgresql+psycopg2",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.hostname,
            port=self.port,
            database=self.database,
        ).render_as_string(hide_password=False)

    def get_procedures_sql(
        self, schema: Optional[str] = None
    ) -> tuple[str, dict]:  # noqa: D102
        if schema is None:
            schema = "public"
        query = f"""
            SELECT routine_name
            FROM information_schema.routines
            WHERE specific_schema = :schema AND routine_type = 'PROCEDURE'
            ORDER BY routine_name;
        """
        return query, {"schema": schema}


class SQLiteSettings(BaseSettings, DialectSettings):
    """Configuration for the 'sqlite' dialect."""

    model_config = SettingsConfigDict(env_prefix="SQLITE_")

    database: Path | Literal[":memory:"]

    def get_connection_url(self) -> str:  # noqa: D102
        if self.database == ":memory:":
            return "sqlite://"
        return URL.create(
            "sqlite", database=str(self.database.resolve())
        ).render_as_string(hide_password=False)


class MySQLSettings(BaseSettings, DialectSettings):
    """Configuration for the 'mysql' dialect."""

    model_config = SettingsConfigDict(env_prefix="MYSQL_")

    hostname: str
    database: str
    username: str
    password: SecretStr
    port: int = 3306

    def get_connection_url(self) -> str:  # noqa: D102
        return URL.create(
            "mysql+pymysql",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.hostname,
            port=self.port,
            database=self.database,
        ).render_as_string(hide_password=False)

    def get_procedures_sql(
        self, schema: Optional[str] = None
    ) -> tuple[str, dict]:  # noqa: D102
        query = """
            SELECT ROUTINE_NAME
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_TYPE = 'PROCEDURE' AND ROUTINE_SCHEMA = :schema
            ORDER BY ROUTINE_NAME;
        """
        return query, {"schema": schema or self.database}


class SnowflakeSettings(BaseSettings, DialectSettings):
    """Configuration for the 'snowflake' dialect."""

    model_config = SettingsConfigDict(env_prefix="SNOWFLAKE_")

    account: str
    username: str
    password: SecretStr
    database: str
    schema_name: str
    warehouse: str
    role: Optional[str] = None

    def get_connection_url(self) -> str:  # noqa: D102
        return URL.create(
            "snowflake",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.account,
            database=f"{self.database}/{self.schema_name}",
            query=clean_dict(
                {
                    "warehouse": self.warehouse,
                    "role": self.role,
                }
            ),
        ).render_as_string(hide_password=False)

    def get_procedures_sql(
        self, schema: Optional[str] = None
    ) -> tuple[str, dict]:  # noqa: D102
        query = """
            SELECT procedure_name
            FROM information_schema.procedures
            WHERE procedure_schema = :schema
            ORDER BY procedure_name;
        """
        return query, {"schema": (schema or self.schema_name).upper()}


class DatabaseManager:
    """A database manager that is agnostic to the underlying dialect."""

    def __init__(self, settings: DialectSettings):
        """Initializes the DatabaseManager.

        Args:
            settings: The dialect-specific settings.
        """
        self._settings = settings
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        """Provides direct access to the underlying SQLAlchemy Engine.

        Returns:
            Engine: The active SQLAlchemy engine instance.

        Raises:
            RuntimeError: If engine is not active.
        """
        if self._engine is None:
            raise RuntimeError("Client is not connected. Please call connect() first.")
        return self._engine

    def connect(self) -> Self:
        """Initializes the SQLAlchemy Engine.

        Returns:
            The instance of the DatabaseManager.
        """
        if self._engine is not None:
            return self
        try:
            logger.info("Initializing SQLAlchemy engine...")
            self._engine = create_engine(self._settings.get_connection_url())
            return self
        except Exception as e:
            logger.error(f"Engine initialization failed: {e}")
            self._engine = None
            raise

    def disconnect(self):
        """Disposes of the SQLAlchemy engine."""
        if self._engine:
            logger.info("Disposing of the SQLAlchemy engine and connection pool.")
            self._engine.dispose()
            self._engine = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def execute_statement(self, sql: str, params: Optional[dict] = None) -> None:
        """Executes an arbitrary SQL statement.

        This method is suitable for operations like CREATE, INSERT, UPDATE,
        DELETE that do not return a result set.

        Args:
            sql: The SQL statement to execute.
            params: Parameters for the SQL statement.
        """
        logger.info(f"Executing statement: {sql[:min(50, len(sql))]}...")
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql), params)
                conn.commit()  # Essential for changes to be saved!
            logger.info("Statement executed successfully.")
        except Exception as e:
            logger.error(f"Error executing statement: {e}")
            raise

    def execute_query(self, sql: str, params: Optional[dict] = None) -> pd.DataFrame:
        """Executes a SQL query and returns results as a DataFrame.

        Args:
            sql: The SQL query to execute.
            params: Parameters for the SQL query.

        Returns:
            A pandas DataFrame with the query results.
        """
        logger.info(f"Executing query: {sql[:min(50, len(sql))]}...")
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(sql), conn, params=params)
            logger.info(f"Query returned {len(df)} rows.")
            return df
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def list_tables(self, schema: Optional[str] = None) -> list[str]:
        """Retrieves a list of table names for a given schema."""
        logger.info(f"Fetching tables for schema: {schema or 'default'}")
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names(schema=schema)
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            raise

    def describe_table(
        self, table_name: str, schema: Optional[str] = None
    ) -> pd.DataFrame:
        """Retrieves column metadata (name, type, etc.) for a specific table."""
        schema_table = f"{schema}.{table_name}" if schema is not None else table_name
        logger.info(f"Describing table: {schema_table}")
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name, schema=schema)
            return pd.DataFrame(columns)
        except Exception as e:
            logger.error(f"Failed to describe table: {e}")
            raise

    def insert_df(
        self,
        df: pd.DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: Literal["fail", "append"] = "fail",
    ) -> None:
        """Performs a fast, bulk insert of a pandas DataFrame into a database table."""
        assert if_exists in ("fail", "append")
        if df.empty:
            logger.warning(
                f"DataFrame is empty, skipping insert into {schema}.{table}."
            )
            return
        logger.info(f"Inserting {len(df)} rows into {schema}.{table}...")
        try:
            df.to_sql(
                name=table,
                con=self.engine,
                schema=schema,
                if_exists=if_exists,
                index=False,
                method="multi",
            )
            logger.info("Bulk insert successful.")
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise

    def list_stored_procedures(self, schema: Optional[str] = None) -> list[str]:
        """Retrieves a list of stored procedure names for a given schema.

        Note: This is often a dialect-specific operation.
        """
        dialect = self.engine.dialect.name
        logger.info(
            f"Fetching stored procedures for schema '{schema}' on dialect '{dialect}'"
        )

        query_info = self._settings.get_procedures_sql(schema=schema)
        if query_info is None:
            logger.warning(
                f"{type(self._settings).__name__} does not support listing stored procedures."
            )
            return []
        query, params = query_info  # Unpack the tuple

        try:
            df = self.execute_query(query, params=params)
            if df.empty:
                return []
            return df.iloc[:, 0].tolist()
        except Exception as e:
            logger.error(f"Failed to list stored procedures: {e}")
            raise
