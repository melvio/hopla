"""
A modules with application wide error handling logic.
"""
import click
from hopla.hoplalib.common import GlobalConstants


class YouFoundABugRewardError(click.ClickException):
    """An exception that helps users submit a bug report.

    Devnote: This is a defensive programming technique.
    """

    def __init__(self, message):
        super().__init__(message=message)

        self.message += ("You found a bug! Impressive work.\n"
                         "Our hardworking volunteers can fix it, if you report it over here:\n "
                         f"{GlobalConstants.NEW_ISSUE_URL}")
