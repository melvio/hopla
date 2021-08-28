import json


class JsonFormatter:
    def __init__(self, json_as_dict: dict):
        self.json_as_dict = json_as_dict

    def format_with_double_quotes(self, indent: int = 2) -> str:
        """format a dictionary such that it has double quotes
        Double quoting allow the string to be used in pipelines

        :param indent:
        :return:
        """
        return json.dumps(self.json_as_dict, indent=indent)
