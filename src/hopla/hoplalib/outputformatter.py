"""
Library code that helps with outputting strings to the CLI user.
"""
import json


class JsonFormatter:
    """
    Class for formatting JSON s.t. it can be used in bash pipelines.
    """
    def __init__(self, json_as_dict: dict):
        self.json_as_dict = json_as_dict

    def format_with_double_quotes(self, indent: int = 2) -> str:
        """format a dictionary such that it has double quotes
        Double quoting allow the string to be used in pipelines

        :param indent:
        :return:
        """
        return json.dumps(self.json_as_dict, indent=indent)
