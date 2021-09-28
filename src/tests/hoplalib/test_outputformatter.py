#!/usr/bin/env python3
import pytest

from hopla.hoplalib.outputformatter import JsonFormatter


class TestJsonFormatter:
    def test___init__(self, json_from_habitica: dict):
        formatter = JsonFormatter(json_from_habitica)

        assert formatter.json_as_dict == json_from_habitica

    def test_format_with_double_quotes(self, json_from_habitica):
        indent = 2
        formatter = JsonFormatter(json_from_habitica)

        result: str = formatter.format_with_double_quotes(indent=indent)

        # I'm using the 'sp' variable name here, because it is also 2 chars long.
        sp: str = ' ' * indent
        assert result == (
            '{\n'
            f'{sp}"success": true,\n'
            f'{sp}"data": -1,\n'
            f'{sp}"message": "You have tamed Shade Velociraptor, let\'s go for a ride!"\n'
            '}'
        )

    @pytest.fixture
    def json_from_habitica(self) -> dict:
        return {
            'success': True, 'data': -1,
            'message': 'You have tamed Shade Velociraptor, let\'s go for a ride!'
        }
