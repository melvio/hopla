"""
A module for filtering python dictionaries
"""
import logging
import sys
from typing import Optional

import click
import jq

log = logging.getLogger()


class JqFilter:
    """Wrapper for `jq` filtering.

    This class ensures consistent usage of jq by multiple commands
    """

    __IDENTITY_FILTER = "."
    """When no filter string is provided we use the no-op filter.

    [Identity Map](https://en.wikipedia.org/wiki/Identity_function)
    """

    def __init__(self, *, jq_filter_spec: Optional[str] = None):
        """Create a JqFilter. Exits when jq cannot compile the filter.


        >>> JqFilter(jq_filter_spec=None).compiled_jq_filter
        jq.compile('.')
        >>> JqFilter(jq_filter_spec=".data | add").compiled_jq_filter
        jq.compile('.data | add')

        :param jq_filter_spec:
        """
        try:

            self.compiled_jq_filter = jq.compile(jq_filter_spec or JqFilter.__IDENTITY_FILTER)
        except ValueError as ex:
            log.debug(ex, exc_info=ex)  # verbose output only for debug level
            click.echo(f"Failed to validate the {jq_filter_spec=}. This is what `jq` had to say: ")
            click.echo(str(ex))
            sys.exit("Exiting: Please provide a different compile string")

    def filter_dict(self, json_dict: dict):
        """Filter the provided json_dict. Exit on failure.

        >>> content_dict = { "userCanOwnQuestCategories" : [ "gold", "hatchingPotion", "pet" ]}
        >>> jq_filter = JqFilter(jq_filter_spec=".userCanOwnQuestCategories")
        >>> jq_filter.filter_dict(content_dict)
        ['gold', 'hatchingPotion', 'pet']

        >>> content_dict = { "buffs": { "int" : 8932 }, "int" : 69 }
        >>> jq_filter = JqFilter(jq_filter_spec="[.buffs.int, .int] | add")
        >>> jq_filter.filter_dict(content_dict)
        9001

        :param json_dict:
        :return:
        """
        # TODO: error handling
        try:
            return self.compiled_jq_filter.input(json_dict).first()
        except ValueError as ex:
            log.debug(ex, exc_info=ex)  # verbose output only for debug level
            click.echo(f"Failed to execute the {self.compiled_jq_filter.input=}.")
            click.echo("This is what `jq` had to say: ")
            click.echo(str(ex))
            sys.exit("Exiting: Please try filtering in a different way")
