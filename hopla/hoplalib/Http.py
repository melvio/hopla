import os
import sys

sys.path.append(os.environ.get("script_dirname"))

# TODO: temporary, while hopla is in beta
try:
    # jetbrains
    from hopla.hoplalib.Authorization import AuthorizationHandler
except:
    # cmdline
    from hoplalib.Authorization import AuthorizationHandler


class RequestHeaders:
    CONTENT_TYPE = "Content-Type"
    CONTENT_TYPE_JSON = "application/json"
    X_CLIENT = "x-client"
    X_API_USER = "x-api-user"
    X_API_KEY = "x-api-key"
    X_CLIENT_VALUE = "79551d98-31e9-42b4-b7fa-9d89b0944319-hopla"

    def __init__(self, auth_parser: AuthorizationHandler = None):
        if auth_parser:
            self.hopla_auth_parser = auth_parser
        else:
            self.hopla_auth_parser = AuthorizationHandler()

    def get_default_request_headers(self):
        return {
            RequestHeaders.CONTENT_TYPE: RequestHeaders.CONTENT_TYPE_JSON,
            RequestHeaders.X_CLIENT: RequestHeaders.X_CLIENT_VALUE,
            RequestHeaders.X_API_USER: self.hopla_auth_parser.user_id,
            RequestHeaders.X_API_KEY: self.hopla_auth_parser.api_token
        }


class UrlBuilder:
    def __init__(self, *,
                 domain: str = "https://habitica.com",
                 api_version: str = "v3",    # probably not the location to be storing this
                 path_extension: str = ""):
        self.domain = domain
        self.api_version = api_version
        self.path_extension = path_extension

    def __str__(self) -> str:
        return f"UrlBuilder(url={self.url})"

    def _get_base_url(self) -> str:
        return f"{self.domain}/api/{self.api_version}"

    @property
    def url(self) -> str:
        return f"{self._get_base_url()}{self.path_extension}"
