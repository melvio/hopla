"""
Library code that helps with outputting strings to the CLI user.
"""
from dataclasses import dataclass
import json


@dataclass
class JsonFormatter:
    """
    Class for formatting JSON s.t. it can be used in bash pipelines.
    """
    json_as_dict: dict

    def format_with_double_quotes(self, indent: int = 2) -> str:
        """format a dictionary such that it has double quotes
        Double quoting allow the string to be used in pipelines

        :param indent:
        :return:
        """
        return json.dumps(self.json_as_dict, indent=indent)
