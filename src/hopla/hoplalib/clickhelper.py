"""
Module with commonly used python-click functionality.
"""
import logging
import datetime
from typing import Optional, Any

import click

log = logging.getLogger()


class EnhancedDate(click.DateTime):
    """EnhancedDate adds 'today' and 'tomorrow' keywords to the click.DateTime type."""
    name = "enhanceddate"

    def __init__(self):
        super().__init__(formats=["%Y-%m-%d", "%d-%m-%Y"])

        # This will add 'today' and 'tomorrow to the help message
        self.formats += ["today", "tomorrow"]

    def convert(self, value: Any,
                param: Optional[click.Parameter],
                ctx: Optional[click.Context]) -> Any:
        """Convert a value provided by the user into a datetime object."""
        if value == "today":
            return datetime.date.today()
        if value == "tomorrow":
            return datetime.date.today() + datetime.timedelta(days=1)

        return super().convert(value, param, ctx)
