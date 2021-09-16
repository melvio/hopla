import random

import pytest
from requests.status_codes import codes
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from hopla.cli.feed import feed
from hopla.hoplalib.zoo.petmodels import PetData


class MockFeedResponse:
    def __init__(self, *, json, status_code: int = 200):
        self.__json = json
        self.status_code = status_code

    def json(self):
        return self.__json


class TestFeedCliCommand:
    # https://habitica.com/apidoc/#api-User-UserFeed

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

    @patch("hopla.cli.feed.FeedPostRequester.post_feed_request")
    def test_feed_pet_once_ok(self, mock_feed_api_call: MagicMock):
        pet_name = "Wolf-Base"
        food_name = "RottenMeat"

        feeding_status_expected = 15
        message_expected = "Sand Sculpture Lion Cub really likes the Rotten Meat!"
        response_content = {"success": True, "data": feeding_status_expected,
                            "message": message_expected, "userV": 59173,
                            "appVersion": "4.205.1"}

        mock_feed_api_call.return_value = MockFeedResponse(json=response_content)

        runner = CliRunner()
        result = runner.invoke(feed, [pet_name, food_name])

        mock_feed_api_call.assert_called_once_with()  # no args
        assert result.exit_code == 0
        assert f'"feeding_status": {feeding_status_expected},' in result.output
        assert f'"message": "{message_expected}"' in result.output

    @pytest.mark.parametrize(
        "pet_name,expected_favorite_food", [
            ("Dolphin-Red", "Strawberry"),
            ("Velociraptor-Shade", "Chocolate"),
            ("Hippo-Skeleton", "Fish"),
            ("Treeling-Zombie", "RottenMeat"),
            ("Pterodactyl-Desert", "Potatoe"),
        ]
    )
    @patch("hopla.cli.feed.FeedPostRequester.post_feed_request")
    def test_feed_pet_with_favorite_food_ok(self, mock_feed_api_call: MagicMock,
                                            pet_name: str,
                                            expected_favorite_food: str):
        feeding_status_expected = 10
        # Side note: This message_expected variable is not perfect because the user' 'text'
        # naming for pets and foods differs often slightly from their 'key'
        # values (e.g. RottenMeat vs. Rotten Meat, DolphinRed vs. Red Dolphin). But that
        # is not relevant here, so we are happy anyways.
        message_expected = f'{pet_name} really likes the {expected_favorite_food}!'
        response_content = {'success': True, 'data': feeding_status_expected,
                            'message': message_expected}
        mock_feed_api_call.return_value = MockFeedResponse(json=response_content)

        runner = CliRunner()
        result = runner.invoke(feed, [pet_name])  # We are not passing any food!

        mock_feed_api_call.assert_called_once_with()  # no args
        assert result.exit_code == 0
        assert f'"feeding_status": {feeding_status_expected},' in result.output
        assert f'"message": "{message_expected}"' in result.output

    @pytest.mark.parametrize(
        "magic_pet_name",
        random.sample(PetData.magic_potion_pet_names, k=30)
    )
    def test_feed_pet_with_favorite_food_no_favorite_food_fail(self, magic_pet_name: str):
        runner = CliRunner()
        result = runner.invoke(feed, [magic_pet_name])

        expected_msg = (f"{magic_pet_name} likes all foods. "
                        "You must specify a FOOD_NAME for this pet.")

        assert result.exit_code == 1
        assert result.output == f"{expected_msg}\n"

    @patch("hopla.cli.feed.FeedPostRequester.post_feed_request")
    def test_feed_pet_once_fail(self, mock_feed_api_call: MagicMock):
        pet_name = "LionCub-SandSculpture"
        food_name = "Strawberry"

        expected_errmsg = "You already have that mount. Try feeding another pet."

        response_content = {
            "success": False,
            "error": "NotAuthorized",
            "message": expected_errmsg
        }
        mock_feed_api_call.return_value = MockFeedResponse(json=response_content,
                                                           status_code=codes.unauthorized)
        runner = CliRunner()
        result = runner.invoke(feed, [pet_name, food_name])

        mock_feed_api_call.assert_called_with()  # no args
        assert result.exit_code == codes.unauthorized
        assert result.stdout == f"{expected_errmsg}\n"
