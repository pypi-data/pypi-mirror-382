import base64
import hashlib
import html
import http.server
import json
import logging
import os
import platform
import queue
import secrets
import socketserver
import sys
import textwrap
import threading
import time
import urllib.parse
import webbrowser
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import StrEnum
from typing import Callable, NotRequired, TypedDict
from urllib.parse import urlencode

import httpx

from ngilive.config import APP_NAME, AUTHORIZE_URL, CLIENT_ID, TOKENS_URL
from ngilive.terminal_helpers import Terminal


def _b64url(n=32) -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(n)).rstrip(b"=").decode()


class AuthError(Exception):
    pass


class TokenResponseBody(TypedDict):
    access_token: str
    expires_in: int
    refresh_expires_in: NotRequired[int]
    refresh_token: NotRequired[str]
    expires_at: NotRequired[float]


def ts(timestamp: float | int):
    dt_local = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone()
    return dt_local.isoformat()


class ITokenCache(ABC):
    @abstractmethod
    def cache_tokens(self, tokens: TokenResponseBody) -> None: ...

    @abstractmethod
    def load_cached_token(self) -> str | None: ...


class TokenCache(ITokenCache):
    def __init__(self, logger) -> None:
        self._logger = logger

        system = platform.system()

        self._logger.debug(f"Selecting cache dir for system type '{system}'")

        if system == "Windows":
            base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            self._user_cache_dir = os.path.join(base, APP_NAME, "Cache")
        elif system == "Darwin":
            self._user_cache_dir = os.path.expanduser(f"~/Library/Caches/{APP_NAME}")
        else:  # Linux / BSD / others
            base = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
            self._user_cache_dir = os.path.join(base, APP_NAME)

        self._logger.debug(f"Selected cache dir '{self._user_cache_dir}'")

    def _get_cache_file(self) -> str:
        cache_dir = self._user_cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, "token.json")

    def cache_tokens(self, tokens: TokenResponseBody):
        # TODO: Better handling of secrets, should not be stored as plain text
        # Minimally restrict permissions for created file. Ideally use keyring
        cache_file_path = self._get_cache_file()
        self._logger.debug(f"Caching tokens at file path: {cache_file_path}")

        tokens["expires_at"] = time.time() + tokens["expires_in"]

        with open(cache_file_path, "w") as f:
            json.dump(tokens, f)

        self._logger.debug(
            f"Successfully cached tokens. Expires at {ts(tokens['expires_at'])}"
        )

    def load_cached_token(self) -> str | None:
        try:
            cache_file_path = self._get_cache_file()
            self._logger.debug(
                f"Attempting to load tokens from cache. File path: {cache_file_path}"
            )
            with open(cache_file_path, "r") as f:
                tokens = json.load(f)

        except FileNotFoundError:
            self._logger.debug("Tokens not loaded from cache. File not found.")
            return None

        if tokens.get("expires_at", 0) > time.time():
            self._logger.debug(
                f"Tokens loaded from cache. Expires at: {ts(tokens['expires_at'])}"
            )
            return tokens["access_token"]

        self._logger.debug("Tokens not loaded from cache. Tokens expired.")
        return None


class OIDC(ABC):
    @abstractmethod
    def tokens(self, tokens_url: str, data: dict) -> TokenResponseBody: ...


class HttpxOIDC(OIDC):
    def __init__(self, logger) -> None:
        self._logger = logger

    def tokens(self, tokens_url: str, data: dict) -> TokenResponseBody:
        self._logger.debug("using code to get tokens...")
        token_response = httpx.post(
            tokens_url,
            data=data,
        )

        try:
            token_response.raise_for_status()
        except Exception as e:
            try:
                self._logger.debug(f"json response: {token_response.json()}")
            except Exception:
                pass

            self._logger.error(e)
            raise AuthError("An error occured when fetching token")

        tokens: TokenResponseBody = token_response.json()
        return tokens


class Auth(ABC):
    def __init__(
        self, loglevel: str, oidc_provider: OIDC | None, token_cache: ITokenCache | None
    ) -> None:
        self._logger = logging.getLogger("ngilive.auth")
        self._logger.setLevel(loglevel)
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter(
                    "[%(asctime)s] %(name)s %(levelname)s: %(message)s",
                    datefmt="%H:%M:%S",
                )
            )
            self._logger.addHandler(handler)

        self._oidc_provider: OIDC
        if oidc_provider is None:
            self._oidc_provider = HttpxOIDC(self._logger)
        else:
            self._oidc_provider = oidc_provider

        self._token_cache: ITokenCache
        if token_cache is None:
            self._token_cache = TokenCache(self._logger)
        else:
            self._token_cache = token_cache

    @abstractmethod
    def get_token(self) -> str: ...


class TCPServer(socketserver.TCPServer):
    # This is needed for the socket server to release the bind on the
    # port as soon as possible
    allow_reuse_address = True


class QueueResult(StrEnum):
    BROWSER_OPEN = "BROWSER_OPEN"
    BROWSER_FAILED = "BROWSER_FAILED"
    CALLBACK_RECEIVED = "CALLBACK_RECEIVED"
    CALLBACK_FAILED = "CALLBACK_FAILED"


def code_handler(
    expected_state: str, queue: queue.Queue[tuple[QueueResult, str]], logger
):
    class CodeHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            code = params.get("code", [None])[0]

            error: str = params.get("error", [""])[0]

            if error != "":
                error += ". "
                keycloak_error_description = params.get("error_description", [""])[0]

                if keycloak_error_description != "":
                    error += keycloak_error_description + ". "

            if params.get("state", [None])[0] != expected_state:
                error += "Invalid state parameter. "

            if not code:
                error += "Could not obtain code for authorization. "

            if error != "":
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    textwrap.dedent(f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="utf-8">
                            <title>{APP_NAME} Authentication</title>
                        </head>
                        <body>
                            <p>
                                {error}
                                You can close this tab.
                            </p>
                        </body>
                        </html>
                    """).encode("utf-8")
                )
                queue.put((QueueResult.CALLBACK_FAILED, error))
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    textwrap.dedent(f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="utf-8">
                            <title>{html.escape(APP_NAME)} Authentication</title>
                        </head>
                        <body>
                            <p>
                                {html.escape(APP_NAME)} authentication successful.
                                You can close this tab.
                            </p>
                        </body>
                        </html>
                    """).encode("utf-8")
                )

                assert code
                queue.put((QueueResult.CALLBACK_RECEIVED, code))

        def log_message(self, format, *args):
            _ = format, args
            logger.debug(
                f"CodeHandler: Callback received from {self.client_address[0]} with path {self.path}"
            )

    return CodeHandler


def generate_pkce_pair():
    # RFC 7636: verifier must be 43–128 chars, unreserved URI characters
    code_verifier = (
        base64.urlsafe_b64encode(os.urandom(64)).rstrip(b"=").decode("utf-8")
    )

    # Compute SHA256 and base64url encode
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())
        .rstrip(b"=")
        .decode("utf-8")
    )
    return code_verifier, code_challenge


def _oidc_browser(url: str, result: queue.Queue[tuple[QueueResult, str]]):
    success = webbrowser.open_new_tab(url)

    if success:
        result.put((QueueResult.BROWSER_OPEN, ""))
    else:
        result.put((QueueResult.BROWSER_FAILED, "Failed to open browser"))


class AuthorizationCode(Auth):
    def __init__(
        self,
        client_id: str = CLIENT_ID,
        authorize_url: str = AUTHORIZE_URL,
        tokens_url: str = TOKENS_URL,
        timeout: int = 300,  # Seconds
        loglevel: str = "INFO",
        oidc_browser: Callable[
            [str, queue.Queue[tuple[QueueResult, str]]], None
        ] = _oidc_browser,
        oidc_provider: OIDC | None = None,
        token_cache: ITokenCache | None = None,
    ) -> None:
        self._client_id = client_id
        self._tokens_url = tokens_url
        self._authorize_url = authorize_url
        self._timeout = timeout
        self._oidc_browser = oidc_browser
        self._result_queue: queue.Queue[tuple[QueueResult, str]] = queue.Queue()

        super().__init__(loglevel, oidc_provider, token_cache)

        self._oidc_provider: OIDC
        if oidc_provider is None:
            self._oidc_provider = HttpxOIDC(self._logger)
        else:
            self._oidc_provider = oidc_provider

        self._token_cache: ITokenCache
        if token_cache is None:
            self._token_cache = TokenCache(self._logger)
        else:
            self._token_cache = token_cache

    def get_token(self) -> str:
        token: str | None = self._token_cache.load_cached_token()
        if token is not None:
            return token

        token = ""

        state = _b64url(16)

        try:
            with TCPServer(
                ("localhost", 0), code_handler(state, self._result_queue, self._logger)
            ) as httpd:
                # TCP Server with port 0 lets the os allocate a free port
                # Here we find which port it picked
                port = httpd.server_address[1]

                code_verifier, code_challenge = generate_pkce_pair()

                redirect_url = f"http://localhost:{port}"

                params = urlencode(
                    {
                        "client_id": self._client_id,
                        "redirect_uri": redirect_url,
                        "response_type": "code",
                        "scope": "email",
                        "code_challenge": code_challenge,
                        "code_challenge_method": "S256",
                        "state": state,
                    }
                )
                authorize_url = f"{self._authorize_url}?{params}"

                threading.Thread(
                    target=self._oidc_browser, args=(authorize_url, self._result_queue)
                ).start()

                status, _ = self._result_queue.get(timeout=10)
                if status != QueueResult.BROWSER_OPEN:
                    raise AuthError("Failed to open browser")

                self._logger.info(
                    "Please complete the authentication in your browser: "
                    f"{Terminal.link(authorize_url, authorize_url)}"
                )
                self._logger.debug(f"Waiting for callback on {redirect_url} ...")

                # Stop listening every second to unblock
                httpd.timeout = 1

                # Listen until timeout
                start, elapsed = time.time(), 0

                while elapsed <= self._timeout:
                    httpd.handle_request()

                    try:
                        status, message = self._result_queue.get_nowait()

                        if status == QueueResult.CALLBACK_FAILED:
                            raise AuthError(message)

                        elif status == QueueResult.CALLBACK_RECEIVED:
                            auth_code = message

                            self._logger.debug("using code to get tokens...")
                            tokens = self._oidc_provider.tokens(
                                self._tokens_url,
                                data={
                                    "grant_type": "authorization_code",
                                    "code": auth_code,
                                    "redirect_uri": redirect_url,
                                    "client_id": self._client_id,
                                    "code_verifier": code_verifier,
                                },
                            )
                            self._logger.debug("tokens successfully obtained")

                            self._token_cache.cache_tokens(tokens)
                            token = tokens["access_token"]
                            break

                    except queue.Empty:
                        pass

                    elapsed = time.time() - start
                    if int(elapsed) % 5 == 0:  # log every 5s
                        self._logger.debug(f"Still waiting... {int(elapsed)}s elapsed")

        except AuthError as e:
            self._logger.error(Terminal.color(str(e), "red"))
            raise e

        except KeyboardInterrupt:
            self._logger.info("get_token interrupted by keyboard")
            raise AuthError("Authentication interrupted by user")

        if not token or token == "":
            raise AuthError("Failed to get token")

        return token


class ClientCredentials(Auth):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tokens_url: str = TOKENS_URL,
        timeout: int = 10,  # Seconds
        loglevel: str = "INFO",
        oidc_provider: OIDC | None = None,
        token_cache: TokenCache | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._tokens_url = tokens_url
        self._timeout = timeout

        super().__init__(loglevel, oidc_provider, token_cache)

    def get_token(self) -> str:
        token: str | None = self._token_cache.load_cached_token()
        if token is not None:
            return token

        tokens = self._oidc_provider.tokens(
            self._tokens_url,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
            },
        )
        self._logger.debug("tokens successfully obtained")

        self._token_cache.cache_tokens(tokens)
        token = tokens["access_token"]
        return token
