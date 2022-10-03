"""
Library code to help with Habitica API HTTPS-requests
"""
from dataclasses import dataclass
from typing import Final

from hopla.hoplalib.authorization import AuthorizationHandler
from hopla.hoplalib.common import GlobalConstants


class RequestHeaders:
    """
    Helper class that takes care of HTTP request headers when interacting with
    the habitica API.

    For more information, see <https://habitica.fandom.com/wiki/Guidance_for_Comrades>
    """
    CONTENT_TYPE_HEADER_NAME = "Content-Type"
    CONTENT_TYPE_HEADER_VALUE_APPLICATION_JSON = "application/json"
    X_CLIENT_HEADER_NAME = "x-client"
    X_API_USER_HEADER_NAME = "x-api-user"
    X_API_KEY_HEADER_NAME = "x-api-key"

    def __init__(self, auth_parser: AuthorizationHandler = None):
        if auth_parser:
            self.hopla_auth_parser = auth_parser
        else:
            self.hopla_auth_parser = AuthorizationHandler()

    def get_default_request_headers(self) -> dict:
        """Return a dict of request headers that are used for nearly every
        habitica API request"""
        return {
            RequestHeaders.CONTENT_TYPE_HEADER_NAME:
                RequestHeaders.CONTENT_TYPE_HEADER_VALUE_APPLICATION_JSON,
            RequestHeaders.X_CLIENT_HEADER_NAME: GlobalConstants.X_CLIENT,
            RequestHeaders.X_API_USER_HEADER_NAME: self.hopla_auth_parser.user_id,
            RequestHeaders.X_API_KEY_HEADER_NAME: self.hopla_auth_parser.api_token
        }


class ResponseHeaders:
    """
    Class with information about Habitica HTTP response headers.
    """
    XRATE_LIMIT_REMAINING_HEADER_NAME: Final[str] = "X-RateLimit-Remaining"
    XRATE_LIMIT_RESET_HEADER_NAME: Final[str] = "X-RateLimit-Reset"


@dataclass(frozen=True)
class UrlBuilder:
    """Helper class for building habitica API URLs."""
    domain: str = GlobalConstants.API_DOMAIN
    api_version: str = GlobalConstants.HABITICA_API_VERSION
    path_extension: str = ""

    def _get_base_url(self) -> str:
        return f"{self.domain}/api/{self.api_version}"

    @property
    def url(self) -> str:
        """Get the build URL"""
        return f"{self._get_base_url()}{self.path_extension}"


@dataclass(repr=True, init=False)
class HabiticaRequest:
    """
    A generic API request class with inheritable logic for specific
    request classes.
    """
    TIMEOUT = 60
    """standard timeout for requests"""

    @property
    def default_headers(self):
        """
        Return the default headers with the user's credentials and the x-client header.
        """
        return RequestHeaders().get_default_request_headers()
