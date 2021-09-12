import pytest
from click.testing import CliRunner

from hopla.cli.feed import FeedPostRequester, feed


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
