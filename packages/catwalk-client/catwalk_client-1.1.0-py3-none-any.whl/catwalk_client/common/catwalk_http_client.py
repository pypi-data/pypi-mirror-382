from os import environ
from json import loads

from urllib.request import Request

from catwalk_client.common.exception import CatwalkClientException

from ._http_client import HTTPClient
from .constants import (
    CATWALK_AUTH_HEADER,
    CATWALK_USER_AGENT_HEADER_VALUE,
    CATWALK_CLIENT_LOCATION,
)


class CatwalkHTTPClient(HTTPClient):
    """Custom Catwalk HTTP client."""

    def __init__(
        self,
        catwalk_url: str,
        auth_token: str,
        insecure: bool = True,
        timeout: int = 30,
        timezone: str = "UTC",
    ):
        """Initialize a `CatwalkHTTPClient` object.

        Args:
            catwalk_url (str): URL of a Catwalk instance.
            auth_token (str): Catwalk authorization token.
            insecure (bool, optional): Whether to use insecure SSL mode.
            Defaults to True.
            timeout (int, optional): Request timeout (in seconds).
            Defaults to 30.
            timezone (str, optional): Timezone name. This value will
            automatically be applied to a `Client-Location` header.
            Defaults to "UTC".
        """
        super().__init__(
            catwalk_url or environ.get("CATWALK_URL"),
            auth_token or environ.get("CATWALK_AUTH_TOKEN"),
            insecure,
            timeout,
        )

        self.timezone = timezone

    def _apply_headers(self, request: Request):
        """Apply default headers.

        Applies `User-Agent`, `Catwalk-Authorization` and `Client-Location`
        headers.

        Args:
            request (Request): `urllib`'s Request object.
        """
        self._add_client_location_header(request)
        self._add_auth_token_header(request, self.auth_token)
        self._add_user_agent_header(request, CATWALK_USER_AGENT_HEADER_VALUE)

    def _add_auth_token_header(self, request: Request, header_value: str = ""):
        """Apply a `Catwalk-Authorization` header to a given request.

        Args:
            request (Request): `urllib`'s Request object.
            header_value (str, optional): Bearer token value. Defaults
            to "".
        """
        request.add_header(CATWALK_AUTH_HEADER, f"Bearer {header_value}")

    def _add_client_location_header(self, request: Request):
        """Apply a `Client-Location` header to a given request.

        Args:
            request (Request): `urllib`'s Request object.
        """
        request.add_header(CATWALK_CLIENT_LOCATION, self.timezone)

    def fetch_auth_token(self, email: str, password: str) -> str:
        """Get authorization token for a given credentials.

        Args:
            email (str): Email of a Catwalk user account.
            password (str): Password to a Catwalk user account.

        Raises:
            CatwalkClientException: On unsuccessful request call.

        Returns:
            str: User's authorization token.
        """
        response, success, _ = self.post(
            "/api/auth/login", {"email": email, "password": password}
        )

        if not success:
            raise CatwalkClientException(response)

        return loads(response)["token"]
