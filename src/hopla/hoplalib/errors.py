"""
A modules with application wide error handling logic.
"""
from dataclasses import dataclass

import click
from hopla.hoplalib.common import GlobalConstants


class YouFoundABugRewardError(click.ClickException):
    """An exception that helps users submit a bug report.

    Devnote: This is a defensive programming technique.
    """

    def __init__(self, message):
        super().__init__(message=self._append_issue_link(message))

    @staticmethod
    def _append_issue_link(message):
        return (f"{message}\nYou found a bug! Impressive work.\n"
                "Our hardworking volunteers can go and fix it, after \n"
                "you report it over here:\n "
                f"{GlobalConstants.NEW_ISSUE_URL}")


@dataclass
class PrintableException(BaseException):
    """A BaseException that implements a default __str__ and __repr__."""

    def __init__(self, msg: str):
        super().__init__(PrintableException.__class__)
        self.msg = msg

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg})"

    def __str__(self) -> str:
        return self.msg
