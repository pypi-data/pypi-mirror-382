import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class APIClient:
    """A client for interacting with a RESTful API.

    This class handles sessions, authentication, and robust error handling.
    Wraps around requests.Session.

    Attributes:
        base_url: The base URL for the API endpoint.
        timeout: The timeout in seconds for requests.
        session: The requests.Session object.
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        """Initializes the API Client.

        Args:
            base_url: The base URL for the API endpoint (e.g., "https://api.example.com").
            headers: A dictionary of headers to include in all requests.
            timeout: The timeout in seconds for requests.
        """
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)

    def set_auth_token(self, token: str, scheme: str = "Token"):
        """Sets an Authorization token header.

        Args:
            token: The authentication token.
            scheme: The authentication scheme (e.g., "Bearer", "Token").
        """
        logger.info(f"Setting auth token with scheme: {scheme}")
        self.session.headers["Authorization"] = f"{scheme} {token}"

    def request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Constructs and sends an API request.

        Args:
            method: The HTTP method (GET, POST, PUT, DELETE).
            endpoint: The API endpoint path.
            **kwargs: Additional keyword arguments for the requests session.

        Returns:
            The JSON response body as a python object, or None if it cant be decoded.

        Raises:
            requests.exceptions.HTTPError: For 4xx/5xx responses.
            requests.exceptions.RequestException: For other request-related errors.
        """
        if self.session is None:
            raise RuntimeError(
                "Session must be initialized before calling this method."
            )
        full_url = f"{self.base_url}{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)

        logger.info(f"Sending {method} request to: {full_url}")
        try:
            response = self.session.request(method, full_url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP Error for {method} {full_url}: {e.response.status_code} {e.response.reason}"
            )
            logger.error(f"Response body: {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {method} {full_url}: {e}")
            raise

    def close(self):
        """Closes the underlying requests session."""
        logger.info("Closing API client session.")
        self.session.close()
        self.session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
