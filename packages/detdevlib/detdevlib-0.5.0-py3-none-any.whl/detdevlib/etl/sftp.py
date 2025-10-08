import logging
import os
import socket
from pathlib import Path
from typing import Optional, Self

import paramiko
from paramiko.sftp_client import SFTPClient
from paramiko.transport import Transport

logger = logging.getLogger(__name__)


class SFTPConnection:
    """An SFTP client for handling file transfers.

    This class supports password and private key authentication.
    """

    def __init__(
        self,
        hostname: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        pkey_path: Optional[str | Path] = None,
        pkey_pass: Optional[str] = None,
        port: int = 22,
    ):
        """Initializes the SFTP connection.

        Credentials can be provided or loaded from environment variables.

        Args:
            hostname: The SFTP hostname.
            username: The SFTP username.
            password: The SFTP password.
            pkey_path: The path to the private key.
            pkey_pass: The passphrase for the private key.
            port: The SFTP port.
        """
        self.hostname = hostname or os.environ.get("SFTP_HOSTNAME")
        self.username = username or os.environ.get("SFTP_USERNAME")
        self.password = password or os.environ.get("SFTP_PASSWORD")
        self.private_key_path = pkey_path or os.environ.get("SFTP_PRIVATE_KEY_PATH")
        self.private_key_passphrase = pkey_pass or os.environ.get(
            "SFTP_PRIVATE_KEY_PASSPHRASE"
        )
        self.port = port

        if self.hostname is None or self.username is None:
            raise ValueError("SFTP hostname and username must be provided.")
        if self.password is None and self.private_key_path is None:
            raise ValueError(
                "Either a password or a private key path must be provided."
            )

        self.transport: Optional[Transport] = None
        self.client: Optional[SFTPClient] = None

    def _check_connection(self):
        """Checks if the client is connected."""
        if not self.client or not self.transport or not self.transport.is_active():
            raise RuntimeError("Not connected to SFTP server. Call connect() first.")

    def connect(self) -> Self:
        """Establishes an SFTP connection.

        Returns:
            The instance of the SFTPConnection.
        """
        if self.transport and self.transport.is_active():
            logger.info("Already connected to SFTP server.")
            return self
        try:
            logger.info(f"Connecting to {self.hostname}:{self.port}...")
            sock = socket.create_connection((self.hostname, self.port), timeout=30)
            self.transport = paramiko.Transport(sock)

            if self.password is not None:
                logger.info(
                    f"Attempting authentication for user '{self.username}' using password."
                )
                self.transport.connect(username=self.username, password=self.password)
            elif self.private_key_path is not None:
                logger.info(
                    f"Attempting authentication for user '{self.username}' using private key."
                )
                pkey = paramiko.RSAKey.from_private_key_file(
                    filename=str(self.private_key_path),
                    password=self.private_key_passphrase,
                )
                self.transport.connect(username=self.username, pkey=pkey)
            else:
                raise ValueError(
                    "Either a password or a private key path must be provided."
                )

            self.client = paramiko.SFTPClient.from_transport(self.transport)
            logger.info("SFTP connection established successfully.")
            return self

        except Exception as e:
            logger.error(f"Failed to connect or authenticate: {e}")
            self.close()  # Ensure resources are cleaned up on failure
            raise

    def close(self):
        """Closes the SFTP connection."""
        if self.client is not None:
            self.client.close()
            self.client = None
        if self.transport is not None:
            self.transport.close()
            self.transport = None
        logger.info("SFTP connection closed.")

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def list_dir(self, remote_path: str) -> list[str]:
        """Lists the contents of a remote directory.

        Args:
            remote_path: The path to the remote directory.

        Returns:
            A list of contents in the directory.
        """
        self._check_connection()
        logger.info(f"Listing directory: {remote_path}")
        try:
            return self.client.listdir(remote_path)
        except FileNotFoundError:
            logger.error(f"Remote directory not found: {remote_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to list directory '{remote_path}': {e}")
            raise

    def exists(self, remote_path: str) -> bool:
        """Checks if a file or directory exists.

        Args:
            remote_path: The path to the remote destination.
        """
        self._check_connection()
        try:
            self.client.stat(remote_path)
            logger.info(f"Path exists: {remote_path}")
            return True
        except FileNotFoundError:
            logger.info(f"Path does not exist: {remote_path}")
            return False
        except Exception as e:
            logger.error(f"Error checking existence of '{remote_path}': {e}")
            raise

    def upload(self, local_path: str | Path, remote_path: str):
        """Uploads a file to the remote server.

        Args:
            local_path: The path to the local file.
            remote_path: The path to the remote destination.
        """
        self._check_connection()
        logger.info(f"Uploading '{local_path}' to '{remote_path}'")
        try:
            self.client.put(str(local_path), remote_path)
            logger.info("Upload successful.")
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise

    def download(self, remote_path: str, local_path: str | Path):
        """Downloads a remote file to the local machine.

        Args:
            remote_path: The path to the remote destination.
            local_path: The path to the local file.
        """
        self._check_connection()
        logger.info(f"Downloading '{remote_path}' to '{local_path}'")
        try:
            self.client.get(remote_path, str(local_path))
            logger.info("Download successful.")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise

    def upload_bytes(self, data: bytes, remote_path: str):
        """Uploads byte data from memory to a remote file.

        Args:
            data: The byte content to upload.
            remote_path: The path to the remote destination.
        """
        self._check_connection()
        logger.info(f"Uploading bytes to '{remote_path}'...")
        try:
            with self.client.open(remote_path, "wb") as f:
                f.write(data)
            logger.info("Byte upload successful.")
        except Exception as e:
            logger.error(f"Byte upload failed: {e}")
            raise

    def download_bytes(self, remote_path: str) -> bytes:
        """Downloads a remote file's content into memory.

        Args:
            remote_path: The path to the remote file.

        Returns:
            The content of the file as bytes.
        """
        self._check_connection()
        logger.info(f"Downloading '{remote_path}' into memory...")
        try:
            with self.client.open(remote_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"In-memory download failed: {e}")
            raise

    def delete(self, remote_path: str):
        """Deletes a file from the remote server.

        Args:
            remote_path: The path to the remote destination.
        """
        self._check_connection()
        logger.info(f"Deleting remote file: {remote_path}")
        try:
            self.client.remove(remote_path)
            logger.info("File deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete file '{remote_path}': {e}")
            raise

    def rename(self, old_remote_path: str, new_remote_path: str):
        """Renames or moves a file on the remote server.

        Args:
            old_remote_path: The path to the remote destination.
            new_remote_path: The path to the new remote destination.
        """
        self._check_connection()
        logger.info(f"Renaming '{old_remote_path}' to '{new_remote_path}'")
        try:
            self.client.rename(old_remote_path, new_remote_path)
            logger.info("Rename successful.")
        except Exception as e:
            logger.error(f"Failed to rename '{old_remote_path}': {e}")
            raise
