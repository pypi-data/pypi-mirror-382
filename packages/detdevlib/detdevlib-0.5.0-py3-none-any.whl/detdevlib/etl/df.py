import csv
import logging
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def tuples_to_df(rows: list[tuple], columns: Iterable[str]) -> pd.DataFrame:
    """Converts a list of tuples into a pandas DataFrame."""
    if not rows:
        return pd.DataFrame(columns=list(columns))
    return pd.DataFrame.from_records(rows, columns=list(columns))


def ndarray_to_df(rows: np.ndarray, columns: Iterable[str]) -> pd.DataFrame:
    """Converts a NumPy ndarray into a pandas DataFrame."""
    return pd.DataFrame(data=rows, columns=list(columns))


def dicts_to_df(
    rows: list[dict], columns: Optional[Iterable[str]] = None
) -> pd.DataFrame:
    """Converts a list of dictionaries (row-oriented) into a pandas DataFrame."""
    return pd.DataFrame.from_records(rows, columns=list(columns) if columns else None)


def excel_to_df(path: bytes | str | Path, **kwargs) -> pd.DataFrame:
    """Reads an Excel file into a pandas DataFrame."""
    if isinstance(path, bytes):
        logger.info("Loading Excel from bytes content.")
        return pd.read_excel(path, **kwargs)
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_excel(path, **kwargs)


def csv_to_df(
    path: str | Path, delimiter: Optional[str] = None, encoding: str = "utf-8", **kwargs
) -> pd.DataFrame:
    """Reads data from a CSV file into a pandas DataFrame, auto-detecting the delimiter."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    logger.info(f"Loading CSV file from: {path}")
    if delimiter is None:
        logger.info("Delimiter not specified, attempting to detect.")
        try:
            with open(path, "r", encoding=encoding) as f:
                delimiter = csv.Sniffer().sniff(f.read(2048)).delimiter
                logger.info(f"Detected delimiter: '{delimiter}'")
        except Exception as e:
            logger.warning(
                f"Could not auto-detect delimiter: {e}. Falling back to default comma ','."
            )
            delimiter = ","

    # Use 'c' engine for performance with single-char delimiters
    engine = "c" if len(delimiter) == 1 else "python"
    kwargs.setdefault("engine", engine)
    return pd.read_csv(path, delimiter=delimiter, encoding=encoding, **kwargs)


def parquet_to_df(path: bytes | str | Path, **kwargs) -> pd.DataFrame:
    """Reads a Parquet file into a pandas DataFrame."""
    logger.info(f"Loading Parquet file from: {path}")
    return pd.read_parquet(path, **kwargs)


def json_to_df(path: str | Path, **kwargs) -> pd.DataFrame:
    """Reads a JSON file into a pandas DataFrame."""
    logger.info(f"Loading JSON file from: {path}")
    return pd.read_json(path, **kwargs)
