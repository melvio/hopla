import pytest
from requests.status_codes import codes
from click.testing import CliRunner
from unittest.mock import patch

from hopla.cli.feed import feed, FeedPostRequester


class TestFeedPostRequester:
    def test_path_is_ok(self):
        pet = "Wolf-Golden"
        food = "Honey"

        feed_requester = FeedPostRequester(pet_name=pet,
                                           food_name=food)

        assert feed_requester.path == f"/user/feed/{pet}/{food}"


class TestFeedCliCommand:
    @pytest.mark.parametrize(
        "pet_name,expected_favorite_food", [
            ("Wolf-Base", "Meat"),
            ("LionCub-SandSculpture", "Any"),
            ("Spider-White", "Milk"),
            ("Spider-Red", "Strawberry"),
            ("Spider-Shade", "Chocolate")
        ]
    )
    def test_list_favorite_food_ok(self, pet_name: str,
                                   expected_favorite_food: str):
        runner = CliRunner()
        result = runner.invoke(feed, [pet_name, "--list-favorite-food"])

        assert result.exit_code == 0
        assert result.output == f"{expected_favorite_food}\n"

    @patch("requests.post")
    def test_feed_pet_once_ok(self, mock_api_call):
        pet_name = "Wolf-Base"
        food_name = "Milk"

        feeding_status_expected = 15
        message_expected = 'Sand Sculpture Lion Cub really likes the Strawberry!'

        class MockResponse:
            def json(self):
                # https://habitica.com/apidoc/#api-User-UserFeed
                return {'success': True, 'data': feeding_status_expected,
                        'message': message_expected, 'userV': 59173,
                        'appVersion': '4.205.1'}

        mock_api_call.return_value = MockResponse()

        runner = CliRunner()
        result = runner.invoke(feed, [pet_name, food_name])

        assert result.exit_code == 0
        assert f'"feeding_status": {feeding_status_expected},' in result.output
        assert f'"message": "{message_expected}"' in result.output

    @patch("requests.post")
    def test_feed_pet_once_fail(self, mock_api_call):
        pet_name = "LionCub-SandSculpture"
        food_name = "Strawberry"

        expected_errmsg = "You already have that mount. Try feeding another pet."

        class MockResponse:
            def __init__(self):
                self.status_code = codes.unauthorized

            def json(self):
                return {
                    "success": False,
                    "error": "NotAuthorized",
                    "message": expected_errmsg
                }

        mock_api_call.return_value = MockResponse()

        runner = CliRunner()
        result = runner.invoke(feed, [pet_name, food_name])

        assert result.exit_code == codes.unauthorized
        assert result.stdout == f"{expected_errmsg}\n"
