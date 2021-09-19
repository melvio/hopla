import pytest
from requests.status_codes import codes
from click.testing import CliRunner, Result
from unittest.mock import patch, MagicMock

from hopla.cli.feed import feed, get_feed_times_until_mount
from hopla.cli.groupcmds.get_user import HabiticaUser


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
        pet_name = "Wolf-Zombie"
        food_name = "RottenMeat"

        feeding_status_expected = 15
        message_expected = f"{pet_name} really likes the Rotten Meat!"
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

    @patch("hopla.cli.feed.HabiticaUserRequest.request_user_data_or_exit")
    @patch("hopla.cli.feed.FeedPostRequester.post_feed_request")
    def test_feed_pet_with_abundant_food(self, mock_feed_request: MagicMock,
                                         mock_user_request: MagicMock):
        most_abundant_food = "Meat"
        magic_pet_name = "PandaCub-Rainbow"

        mock_user_request.return_value = HabiticaUser({
            "items": {"food": {most_abundant_food: 10, "Honey": 4}}
        })

        expected_feed_data = 10
        expected_msg = f"{magic_pet_name} really likes the {most_abundant_food}!"
        success_response = {
            "success": True,
            "data": expected_feed_data,
            "message": expected_msg
        }
        mock_feed_request.return_value = MockFeedResponse(json=success_response)

        runner = CliRunner()
        result: Result = runner.invoke(feed, [magic_pet_name])

        assert result.exit_code == 0
        assert f'"feeding_status": {expected_feed_data}' in result.stdout
        assert f'"message": "{expected_msg}"' in result.stdout

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
        result: Result = runner.invoke(feed, [pet_name, food_name])

        mock_feed_api_call.assert_called_with()  # no args

        # TODO: https://github.com/melvio/hopla/issues/104
        assert result.exit_code == codes.unauthorized
        assert result.stdout == f"{expected_errmsg}\n"

    def test_cannot_specify_times_and_until_mount(self):
        runner = CliRunner()
        result = runner.invoke(feed, ["Rat-Red", "--until-mount", "--times", 2])

        expected_errmsg = "Conflicting options: Cannot specify both --times and --until-mount"
        assert expected_errmsg in result.stdout
        assert result.exit_code == 2

    @patch("hopla.cli.feed.HabiticaUserRequest.request_user_data_or_exit")
    def test_get_feed_data_until_mount_ok(self, mock_user_request: MagicMock):
        pet_name = "Rat-Red"
        food_name = "Strawberry"
        feed_status = 21
        mock_user_request.return_value = HabiticaUser({"items": {"pets": {pet_name: feed_status},
                                                                 "mounts": {}}})

        result: int = get_feed_times_until_mount(pet_name, food_name)

        expected_strawberries = 6
        assert result == expected_strawberries

    @patch("hopla.cli.feed.HabiticaUserRequest.request_user_data_or_exit")
    def test_get_feed_data_until_mount_no_pet_fail(self,
                                                   mock_user_request: MagicMock):
        pet_name = "Rat-Red"
        food_name = "Strawberry"
        mock_user_request.return_value = HabiticaUser({"items": {"pets": {},
                                                                 "mounts": {}}})

        with pytest.raises(SystemExit) as execinfo:
            get_feed_times_until_mount(pet_name, food_name)

        err_msg = str(execinfo.value)
        assert err_msg == f"Can't feed pet {pet_name}. You don't have this pet."

    @patch("hopla.cli.feed.HabiticaUserRequest.request_user_data_or_exit")
    def test_get_feed_data_until_mount_have_mount_fail(self,
                                                       mock_user_request: MagicMock):
        pet_name = "Rat-Red"
        food_name = "Strawberry"
        feed_status = -1
        mock_user_request.return_value = HabiticaUser(
            {"items": {"pets": {pet_name: feed_status},
                       "mounts": {pet_name: True}}}
        )

        with pytest.raises(SystemExit) as execinfo:
            get_feed_times_until_mount(pet_name, food_name)

        err_msg = str(execinfo.value)
        assert err_msg == f"Can't feed pet {pet_name}. You have the mount."

    @patch("hopla.cli.feed.HabiticaUserRequest.request_user_data_or_exit")
    def test_get_feed_data_until_mount_pet_unfeedable_data(self,
                                                           mock_user_request: MagicMock):
        pet_name = "Phoenix-Base"  # unfeedable
        food_name = "Strawberry"
        feed_status = 5
        mock_user_request.return_value = HabiticaUser(
            {"items": {"pets": {pet_name: feed_status},
                       "mounts": {}}}
        )

        with pytest.raises(SystemExit) as execinfo:
            get_feed_times_until_mount(pet_name, food_name)

        err_msg = str(execinfo.value)
        assert f"Can't feed pet {pet_name}." in err_msg

    @patch("hopla.cli.feed.FeedPostRequester")
    @patch("hopla.cli.feed.HabiticaUserRequest.request_user_data_or_exit")
    def test_feed_until_mount(self,
                              mock_user_request: MagicMock,
                              mock_feed_requester: MagicMock):
        pet_name = "Egg-Shade"
        food_name = "Strawberry"
        feed_status = 47
        mock_user_request.return_value = HabiticaUser(
            {"items": {"pets": {pet_name: feed_status},
                       "mounts": {}}}
        )

        response_msg = f"You have tamed {pet_name}, let's go for a ride!"
        response_data = -1

        # This is not the prettiest ways of solving this. Feel free
        # to refactor this mocking logic.
        class MockRequester:
            class MockResponse:
                def json(self):
                    return {"success": True, "data": response_data,
                            "message": response_msg}

            def post_feed_request(self):
                return MockRequester.MockResponse()

        mock_feed_requester.return_value = MockRequester()

        runner = CliRunner()
        result: Result = runner.invoke(feed, [pet_name, food_name, "--until-mount"])

        expected_feed_times = 2
        mock_feed_requester.assert_called_with(
            pet_name=pet_name,
            food_name=food_name,
            food_amount=expected_feed_times
        )
        assert result.exit_code == 0
        assert response_msg in result.stdout
        assert f'"feeding_status": {response_data}' in result.stdout
