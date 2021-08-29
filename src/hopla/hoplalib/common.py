from typing import Final


class GlobalConstants:
    """Class of global variables to be used by the entire application.

    Note that some of these constant may be upgraded to configuration parameters.
    """
    HABITICA_API_VERSION: Final[str] = "v3"
    API_DOMAIN: Final[str] = "https://habitica.com"
    DEVELOPMENT_UUID: Final[str] = "79551d98-31e9-42b4-b7fa-9d89b0944319"
    X_CLIENT: Final[str] = f"{DEVELOPMENT_UUID}-hopla"
