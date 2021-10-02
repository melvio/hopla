#!/usr/bin/env python3
"""
Module with tasks models.
"""
from dataclasses import dataclass
import datetime
from typing import Dict, List, Optional


class TaskDifficultyData:
    """Class with task difficulty data."""
    DIFFICULTIES_SCORE_MAPPING: Dict[str, str] = {
        "hard": "2", "medium": "1.5", "easy": "1", "trivial": "0.1"
    }
    VALID_DIFFICULTIES: List[str] = list(DIFFICULTIES_SCORE_MAPPING.keys())
    """Habitica task difficulties. See https://habitica.com/apidoc/#api-Task-CreateUserTasks."""


class HabiticaChecklist:
    """ Habitica Checklist """

    def __init__(self, *, checklist: Optional[List[str]] = None):
        self.checklist = checklist or []

    def __repr__(self) -> object:
        return self.__class__.__name__ + f"(checklist={self.checklist})"

    def is_empty(self) -> bool:
        """Return true if the checklist is empty.

        >>> HabiticaChecklist(checklist=[]).is_empty()
        True
        >>> HabiticaChecklist(checklist=["item 1"]).is_empty()
        False

        """
        return self.checklist is None or len(self.checklist) == 0

    def to_json_list(self) -> List[Dict[str, str]]:
        """Turn a checklist into a list that we can pass to the habitica API"""
        return [{"text": line} for line in self.checklist]


@dataclass
class HabiticaTodo:
    """ Habitica To-Do"""

    def __init__(self, *,
                 todo_name: str,
                 difficulty: str,
                 due_date: Optional[datetime.datetime] = None,
                 checklist: Optional[HabiticaChecklist] = None):
        self.todo_name = todo_name
        self._type = "todo"
        self.difficulty = difficulty
        self.due_date = due_date
        self.checklist: HabiticaChecklist = checklist or HabiticaChecklist()

    def difficulty_to_score(self) -> str:
        """Return score for the To-Do's difficulty.

        >>> hab_todo = HabiticaTodo(todo_name="my-task", difficulty="easy")
        >>> hab_todo.difficulty_to_score()
        '1'
        >>> hab_todo.difficulty = "trivial"
        >>> hab_todo.difficulty_to_score()
        '0.1'

        :raise KeyError in case of an invalid difficulty
        """
        return TaskDifficultyData.DIFFICULTIES_SCORE_MAPPING[self.difficulty]

    def due_date_to_date_str(self) -> str:
        """Turn the due_date into a valid ISO 8601 date format

        >>> hab_todo = HabiticaTodo(todo_name="my-task", difficulty="easy",\
                                    due_date=datetime.datetime(day=31, month=1, year=2069))
        >>> hab_todo.due_date_to_date_str()
        '2069-01-31'
        """
        habitica_date_format = "%Y-%m-%d"
        return self.due_date.strftime(habitica_date_format)

    def to_json_dict(self) -> dict:
        """Turn an instance of this class into a dict that we can pass to the habitica API.

        >>> hab_todo = HabiticaTodo(todo_name="my-task", difficulty="medium",\
                                    checklist=HabiticaChecklist(checklist=["myitem"]))
        >>> hab_todo.to_json_dict()
        {'text': 'my-task', 'type': 'todo', 'priority': '1.5', 'checklist': [{'text': 'myitem'}]}
        """
        todo_dict = {
            "text": self.todo_name,
            "type": self._type,
            "priority": self.difficulty_to_score(),
            "checklist": self.checklist.to_json_list()
        }

        if self.due_date:
            todo_dict["date"] = self.due_date_to_date_str()

        return todo_dict
