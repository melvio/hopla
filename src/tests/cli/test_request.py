#!/usr/bin/env python3

from hopla.cli.request import display_response


class MockOkResponse:
    """
    This mock response was derived from a HTTP GET request to /api/v3/status.
    """

    def json(self):
        return {
            "success": True, "data": {"status": "up"}, "appVersion": "4.234.0"
        }

    @property
    def status_code(self) -> int:
        return 200

    @property
    def headers(self):
        """Most of the headers retrieved from Habitica (but not all). Also changed the date"""
        access_control_allow_headers = (
            "Authorization,Content-Type,Accept,"
            "Content-Encoding,X-Requested-With,x-api-user,x-api-key,x-client"
        )
        access_control_expose_headers = (
            "X-RateLimit-Limit,X-RateLimit-Remaining,"
            "X-RateLimit-Reset,Retry-After"
        )
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,HEAD,DELETE",
            "Access-Control-Allow-Headers": access_control_allow_headers,
            "Access-Control-Expose-Headers": access_control_expose_headers,
            "X-RateLimit-Limit": 30,
            "X-RateLimit-Remaining": 29,
            "X-RateLimit-Reset": "Mon Oct 16 2022 13:49:39 GMT+0000 (Coordinated Universal Time)",
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": 62,
            "Vary": "Accept-Encoding",
            "Date": "Mon, 16 Oct 2022 13:48:39 GMT"
        }


class TestDisplayResponse:
    def test_display_response_normal_case(self, capsys):
        response = MockOkResponse()
        display_response(response,
                         show_response_headers=False,
                         show_status_code=False,
                         show_response=True)

        captured = capsys.readouterr()
        assert "RESPONSE HEADERS" not in captured.out
        assert "X-RateLimit-Limit: 30" not in captured.out
        assert "HTTP Status Code: " not in captured.out
        assert captured.out == (
            '{\n'
            '  "success": true,\n'
            '  "data": {\n'
            '    "status": "up"\n'
            '  },\n'
            '  "appVersion": "4.234.0"\n'
            '}\n'
        )
        assert captured.err == ""

    def test_display_response_show_only_headers(self, capsys):
        response = MockOkResponse()
        display_response(response,
                         show_response_headers=True,
                         show_status_code=False,
                         show_response=False)

        captured = capsys.readouterr()
        assert "RESPONSE HEADERS" in captured.out
        assert "X-RateLimit-Limit: 30" in captured.out
        assert "HTTP Status Code: " not in captured.out
        assert ('{\n'
                '  "success": true,\n'
                '  "data": {\n'
                '    "status": "up"\n'
                '  },\n'
                '  "appVersion": "4.234.0"\n'
                '}\n'
                ) not in captured.out
        assert captured.err == ""

    def test_display_response_show_only_status_code(self, capsys):
        response = MockOkResponse()
        display_response(response,
                         show_response_headers=False,
                         show_status_code=True,
                         show_response=False)

        captured = capsys.readouterr()
        assert "RESPONSE HEADERS" not in captured.out
        assert "X-RateLimit-Limit: 30" not in captured.out
        assert all(header not in captured.out for header in response.json().keys())
        assert f"HTTP Status Code: {response.status_code}" in captured.out

        assert ('{\n'
                '  "success": true,\n'
                '  "data": {\n'
                '    "status": "up"\n'
                '  },\n'
                '  "appVersion": "4.234.0"\n'
                '}\n'
                ) not in captured.out
        assert captured.err == ""

    def test_display_response_show_headers_show_content_show_status_ok(self, capsys):
        response = MockOkResponse()
        display_response(response,
                         show_response_headers=True,
                         show_status_code=True,
                         show_response=True)

        captured = capsys.readouterr()
        assert "RESPONSE HEADERS" in captured.out
        assert "X-RateLimit-Limit: 30" in captured.out
        assert "HTTP Status Code: " in captured.out
        assert ('{\n'
                '  "success": true,\n'
                '  "data": {\n'
                '    "status": "up"\n'
                '  },\n'
                '  "appVersion": "4.234.0"\n'
                '}\n'
                ) in captured.out
        assert captured.err == ""

    def test_display_response_show_nothing(self, capsys):
        response = MockOkResponse()
        display_response(response,
                         show_response_headers=False,
                         show_status_code=False,
                         show_response=False)

        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""
