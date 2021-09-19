"""
Module with commonly used python-click functionality.
"""
import logging
import datetime
from typing import List, Optional, Any

import click

log = logging.getLogger()




def case_insensitive_aliases(argument: str, choices: List[str], *,
                             raise_if_not_found=False):
    """Takes a potentially in-properly cased argument and returns
       the properly cased version"""
    # This function works but it very ugly:
    # @click.command(context_settings=dict(
    #       token_normalize_func= lambda x: case_insensitive_aliases(x, valid_food_names))
    # )

    for choice in choices:
        if argument.lower() == choice.lower():
            return choice

    if raise_if_not_found:
        raise ValueError(f"Could not match argument={argument} with choices={choices}")
    return argument


class EnhancedDate(click.DateTime):
    """EnhancedDate adds 'today' and 'tomorrow' keywords to the click.DateTime type."""
    name = "enhanceddate"

    def __init__(self):
        super().__init__(formats=["%Y-%m-%d", "%d-%m-%Y"])

        # This will add 'today' and 'tomorrow to the help message
        self.formats += ["today", "tomorrow"]

    def convert(self, value: Any, param: Optional["Parameter"], ctx: Optional["Context"]) -> Any:
        """Convert a value provided by the user into a datetime object."""
        if value == "today":
            return datetime.date.today()
        if value == "tomorrow":
            return datetime.date.today() + datetime.timedelta(days=1)

        return super().convert(value, param, ctx)
