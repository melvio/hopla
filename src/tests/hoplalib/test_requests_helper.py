#!/usr/bin/env python3
from unittest.mock import MagicMock
import pytest

import requests

from hopla.hoplalib.requests_helper import get_data_or_exit


class TestRequestHelperModule:

    def test_get_data_or_exit_ok(self):
        test_user_data = {"achievements": {"streak": 195}}
        valid_mock_user_dict = {"success": True, "data": test_user_data}

        response = requests.Response()
        response.json = MagicMock(return_value=valid_mock_user_dict)

        result = get_data_or_exit(api_response=response)

        response.json.assert_called_once()
        assert result == test_user_data

    def test_get_data_or_exit_fail(self):
        errmsg = "Don't worry, happens to the best of us."
        error_response = {
            "success": False,
            "error": "BadRequest",
            "message": errmsg,
        }

        response = requests.Response()
        response.json = MagicMock(return_value=error_response)
        response.status_code = 400

        with pytest.raises(SystemExit) as ex:
            get_data_or_exit(response)

        response.json.assert_called_once()
        expected_exit_msg = f"The habitica API call failed: status_code={response.status_code}"
        assert ex.value.code == expected_exit_msg
