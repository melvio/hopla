#!/usr/bin/env python3
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner, Result

from hopla.cli.add.todo import todo
from hopla.hoplalib.tasks.taskmodel import HabiticaTodo


class MockAddTodoRequest:
    def __init__(self, mocked_response: dict):
        self.mocked_response = mocked_response

    def post_add_todo_request(self) -> dict:
        return self.mocked_response


class TestTodoCliCommand:
    @patch("hopla.cli.add.todo.AddTodoRequest")
    def test_todo_name_only_task(self,
                                 todo_request_mock: MagicMock,
                                 todo_name: str,
                                 mock_todo_response: dict):
        todo_request_mock.return_value = MockAddTodoRequest(mock_todo_response)
        runner = CliRunner()
        result: Result = runner.invoke(todo, [todo_name])

        todo_request_mock.assert_called_with(
            habitica_todo=HabiticaTodo(difficulty="easy",
                                       todo_name=todo_name)
        )
        assert result.exit_code == 0

    @patch("hopla.cli.add.todo.AddTodoRequest")
    def test_todo_no_task_name(self,
                               todo_request_mock: MagicMock,
                               mock_todo_response: dict):
        todo_request_mock.return_value = MockAddTodoRequest(mock_todo_response)
        runner = CliRunner()
        user_input = "cure rhabdomyolysis"
        result: Result = runner.invoke(todo, input=user_input)

        todo_request_mock.assert_called_with(
            habitica_todo=HabiticaTodo(difficulty="easy",
                                       todo_name=user_input)
        )
        assert result.exit_code == 0

    @patch("hopla.cli.add.todo.AddTodoRequest")
    def test_todo_today_option(self,
                               todo_request_mock: MagicMock,
                               todo_name: str,
                               mock_todo_response: dict):
        todo_request_mock.return_value = MockAddTodoRequest(mock_todo_response)
        runner = CliRunner()
        result: Result = runner.invoke(todo, [todo_name, "--today"])

        todo_request_mock.assert_called_with(
            habitica_todo=HabiticaTodo(difficulty="easy",
                                       due_date=datetime.today(),
                                       todo_name=todo_name)
        )
        assert result.exit_code == 0

    @patch("hopla.cli.add.todo.AddTodoRequest")
    def test_todo_tomorrow_option(self,
                                  todo_request_mock: MagicMock,
                                  todo_name: str,
                                  mock_todo_response: dict):
        todo_request_mock.return_value = MockAddTodoRequest(mock_todo_response)
        runner = CliRunner()
        result: Result = runner.invoke(todo, [todo_name, "--tomorrow"])

        tomorrow: datetime = datetime.today() + timedelta(days=1)
        todo_request_mock.assert_called_with(
            habitica_todo=HabiticaTodo(difficulty="easy",
                                       due_date=tomorrow,
                                       todo_name=todo_name)
        )
        assert result.exit_code == 0

    @pytest.mark.parametrize("cmd_due_date,expected_datetime", [
        ("2021-01-02", datetime(year=2021, month=1, day=2)),
        ("1969-12-10", datetime(year=1969, month=12, day=10)),
        ("01-05-2042", datetime(year=2042, month=5, day=1)),
        ("07-11-3012", datetime(year=3012, month=11, day=7))
    ])
    @patch("hopla.cli.add.todo.AddTodoRequest")
    def test_todo_due_date_option(self,
                                  todo_request_mock: MagicMock,
                                  cmd_due_date: str,
                                  expected_datetime: datetime,
                                  todo_name: str,
                                  mock_todo_response: dict):
        todo_request_mock.return_value = MockAddTodoRequest(mock_todo_response)
        runner = CliRunner()
        date_arg = "2021-01-02"
        result: Result = runner.invoke(todo, [todo_name, "--due-date", date_arg])

        todo_request_mock.assert_called_with(
            habitica_todo=HabiticaTodo(difficulty="easy",
                                       due_date=datetime(day=2, month=1, year=2021),
                                       todo_name=todo_name)
        )
        assert result.exit_code == 0

    @pytest.fixture()
    def todo_name(self) -> str:
        return "my_todo"

    @pytest.fixture
    def mock_todo_response(self, todo_name: str) -> dict:
        return {
            "challenge": {},
            "group": {
                "approval": {"required": False, "approved": False, "requested": False},
                "assignedUsers": [], "sharedCompletion": "singleCompletion"
            },
            "completed": False,
            "collapseChecklist": False,
            "type": "todo",
            "notes": "",
            "tags": [],
            "value": 0,
            "priority": 1,
            "attribute": "str",
            "byHabitica": False,
            "text": todo_name,
            "checklist": [],
            "date": "2021-10-03T00:00:00.000Z",
            "reminders": [],
            "_id": "cc00e66e-8dcc-4218-b675-3119ebda00c6",
            "createdAt": "2021-10-02T07:55:02.893Z",
            "updatedAt": "2021-10-02T07:55:02.893Z",
            "userId": "79213ab8-31e9-42b4-b7fa-9d89b0114319",
            "id": "cc78326e-8dcc-4298-b675-3d000bda00c6"
        }
