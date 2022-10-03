#!/usr/bin/env python3
"""
The module with controllers for habitica tasks.
"""
import requests

from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.tasks.taskmodel import HabiticaTodo


class AddTodoRequest(HabiticaRequest):
    """An object that can perform an add To-Do request"""

    def __init__(self, habitica_todo: HabiticaTodo):
        self.url: str = UrlBuilder(path_extension="/tasks/user").url
        self.habitica_todo = habitica_todo

    def post_add_todo_request(self):
        """Perform the add To-Do request and return the data in case of success"""
        response = requests.post(
            url=self.url,
            headers=self.default_headers,
            json=self.habitica_todo.to_json_dict(),
            timeout=HabiticaRequest.TIMEOUT
        )
        return get_data_or_exit(response)
