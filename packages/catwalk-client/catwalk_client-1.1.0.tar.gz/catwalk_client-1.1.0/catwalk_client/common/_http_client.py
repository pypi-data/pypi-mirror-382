from __future__ import annotations

from json import loads, dumps
from ssl import SSLContext, CERT_NONE, create_default_context
from typing import Any, Mapping, Sequence, Tuple, Union

from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen, Request

QueryType = Union[
    Mapping[Any, Any],
    Mapping[Any, Sequence[Any]],
    Sequence[Tuple[Any, Any]],
    Sequence[Tuple[Any, Sequence[Any]]],
]


class HTTPClient:
    """HTTP client that uses `urllib` to execute requests."""

    def __init__(
        self, url: str, auth_token: str, insecure: bool = True, timeout: int = 30
    ):
        """Initialize HTTPClient object.

        Args:
            url (str): URL to which future request will be made.
            auth_token (str): Bearer authorization token.
            insecure (bool, optional): Whether to use insecure SSL mode.
            Defaults to True.
            timeout (int, optional): Request timeout (in seconds).
            Defaults to 30.
        """
        self.url = url
        self.auth_token = auth_token
        self.insecure = insecure
        self.timeout = timeout

    def get_url(self, path: str) -> str:
        """Return full URL.

        Args:
            path (str): URL path (must begin with `/`).

        Returns:
            str: Full URL path e.g. `http://localhost/test-endpoint` where
            `/test-endpoint` is a given path string and `http://localhost`
            is client's configuration URL.
        """
        return self.url.rstrip("/") + path

    def get(
        self,
        url_postfix: str,
        query_params: QueryType | None = None,
        doseq: bool = False,
    ) -> tuple[str, bool, int]:
        """Makes an HTTP GET call.

        Args:
            url_postfix (str): URL endpoint path.
            query_params (QueryType | None, optional): URL query params.
            Defaults to None.
            doseq (bool, optional): If any values in the query arg are
            sequences and `doseq` is `True`, each sequence element is
            converted to a separate parameter. Defaults to False.

        Returns:
            tuple[str, bool, int]: Returns three values in form of a tuple:
            response data/message in form of a string, boolean value that
            informs if the request was executed successfully and a response
            status code.
        """
        url = self.get_url(url_postfix) + self._encode_query_params(query_params, doseq)
        req = Request(url=url)
        return self._make_request(req)

    def post(
        self,
        url_postfix: str,
        payload: dict | None,
        query_params: QueryType | None = None,
        doseq: bool = False,
    ) -> tuple[str, bool, int]:
        """Makes an HTTP POST call.

        Args:
            url_postfix (str): URL endpoint path.
            payload (dict | None): Request's body.
            query_params (QueryType | None, optional): URL query params.
            Defaults to None.
            doseq (bool, optional): If any values in the query arg are
            sequences and `doseq` is `True`, each sequence element is
            converted to a separate parameter. Defaults to False.

        Returns:
            tuple[str, bool, int]: Returns three values in form of a tuple:
            response data/message in form of a string, boolean value that
            informs if the request was executed successfully and a response
            status code.
        """
        req_data = dumps(payload).encode() if payload else b""
        url = self.get_url(url_postfix) + self._encode_query_params(query_params, doseq)
        req = Request(url=url, data=req_data)
        req.add_header("Content-Type", "application/json")
        return self._make_request(req)

    def patch(
        self,
        url_postfix: str,
        payload: dict | None,
        query_params: QueryType | None = None,
        doseq: bool = False,
    ) -> tuple[str, bool, int]:
        """Makes an HTTP PATCH call.

        Args:
            url_postfix (str): URL endpoint path.
            payload (dict | None): Request's body.
            query_params (QueryType | None, optional): URL query params.
            Defaults to None.
            doseq (bool, optional): If any values in the query arg are
            sequences and `doseq` is `True`, each sequence element is
            converted to a separate parameter. Defaults to False.

        Returns:
            tuple[str, bool, int]: Returns three values in form of a tuple:
            response data/message in form of a string, boolean value that
            informs if the request was executed successfully and a response
            status code.
        """
        req_data = dumps(payload).encode() if payload else b""
        url = self.get_url(url_postfix) + self._encode_query_params(query_params, doseq)
        req = Request(url=url, data=req_data, method="PATCH")
        req.add_header("Content-Type", "application/json")
        return self._make_request(req)

    def _make_request(self, request: Request) -> tuple[str, bool, int]:
        """Execute given request.

        Args:
            request (Request): `urllib`'s Request object.

        Returns:
            tuple[str, bool, int]: Returns three values in form of a tuple:
            response data/message in form of a string, boolean value that
            informs if the request was executed successfully and a response
            status code.
        """
        self._apply_headers(request)
        try:
            resp = urlopen(
                request, timeout=self.timeout, context=self._get_ssl_context()
            )
        except HTTPError as e:
            e_body = self._parse_http_error(e)
            return (
                f"Error: {e}\n[URL] {e.geturl()}\n[DETAILS] {e_body}",
                False,
                e.getcode(),
            )
        except URLError as e:
            return f"Connection error: {e.reason}", False, -1
        except ConnectionResetError as e:
            return f"Connection reset error: {e}", False, -1
        except Exception as e:
            return f"Error: {e}", False, -1

        return resp.read().decode(), True, resp.getcode()

    def _parse_http_error(self, error: HTTPError) -> str | dict | None:
        """Parse HTTP response error body. Handles `text/html` and `application/json`.

        Args:
            error (HTTPError): Request response error.

        Returns:
            str | dict | None: Decoded response error body. Returns None if
            `Content-Type` of given response isn't either a `text/html` or
            an `application/json`.
        """
        content_type = error.headers.get_content_type()

        if content_type == "application/json":
            return self._parse_http_error_json(error)
        elif content_type == "text/html":
            return self._parse_http_error_html(error)

        return None

    def _parse_http_error_json(self, error: HTTPError) -> dict:
        """Parse HTTP error with `Content-Type: application/json`.

        Args:
            error (HTTPError): Request response error.

        Returns:
            dict: Decoded response error JSON body.
        """
        return loads(error.read().decode())

    def _parse_http_error_html(self, error: HTTPError) -> str:
        """Parse HTTP error with `Content-Type: text/html`.

        Args:
            error (HTTPError): Request response error.

        Returns:
            str: Decoded response error HTML body.
        """
        return error.read().decode()

    def _get_ssl_context(self) -> SSLContext:
        """Get request's SSL context. If `HTTPClient.insecure` is set to
        `True` it won't validate the hostname and the certificate.

        Returns:
            SSLContext: SSL context.
        """
        ctx = create_default_context()
        if self.insecure:
            ctx.check_hostname = False
            ctx.verify_mode = CERT_NONE
        return ctx

    def _encode_query_params(
        self, query_params: QueryType | None, doseq: bool = False
    ) -> str:
        """Encode HTTP query parameters.

        Args:
            query_params (QueryType | None): Query parameters in form of
            a mapping or sequence.
            doseq (bool, optional): If any values in the query arg are
            sequences and `doseq` is `True`, each sequence element is
            converted to a separate parameter. Defaults to False.

        Returns:
            str: Encoded query parameters in form of a string. It
            automatically adds the `?` as a prefix.
        """
        if query_params is None or len(query_params) == 0:
            return ""
        encoded_params = urlencode(query=query_params, doseq=doseq)
        return "?" + encoded_params

    def _apply_headers(self, request: Request):
        """Apply default headers.

        Applies `User-Agent` and `Authorization` headers.

        Args:
            request (Request): `urllib`'s Request object.
        """
        self._add_user_agent_header(request)
        self._add_auth_token_header(request, self.auth_token)

    def _add_auth_token_header(self, request: Request, header_value: str = ""):
        """Apply an `Authorization` header to a given request.

        Args:
            request (Request): `urllib`'s Request object.
            header_value (str, optional): Bearer token value.
            Defaults to "".
        """
        request.add_header("Authorization", f"Bearer {header_value}")

    def _add_user_agent_header(
        self, request: Request, header_value: str = "Request/1.0"
    ):
        """Apply a `User-Agent` header to a given request.

        Args:
            request (Request): `urllib`'s Request object.
            header_value (str, optional): User agent information.
            Defaults to "Request/1.0".
        """
        if not request.has_header("User-Agent"):
            request.add_header("User-Agent", header_value)
