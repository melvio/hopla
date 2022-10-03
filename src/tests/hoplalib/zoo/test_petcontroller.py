#!/usr/bin/env python3
from unittest.mock import MagicMock, patch

import pytest

from hopla.hoplalib.zoo.petcontroller import FeedPostRequester
from hopla.hoplalib.zoo.zoofeed_algorithms import FeedPlanItem


class TestFeedPostRequester:
    def test_path_is_ok(self):
        pet = "Wolf-Golden"
        food = "Honey"

        feed_requester = FeedPostRequester(pet_name=pet,
                                           food_name=food)

        assert feed_requester.path == f"/user/feed/{pet}/{food}"

    def test_url_is_okay(self):
        pet = "Wolf-Shimmer"
        food = "Meat"

        feed_requester = FeedPostRequester(pet_name=pet,
                                           food_name=food)

        result_url = feed_requester.feed_pet_food_url

        expected_url = f"https://habitica.com/api/v3/user/feed/{pet}/{food}"
        assert result_url == expected_url

    @pytest.mark.parametrize("times,expected_times", [(2, 2), (None, 1)])
    @patch("hopla.hoplalib.zoo.petcontroller.HabiticaRequest.default_headers")
    @patch("hopla.hoplalib.zoo.petcontroller.requests.post")
    def test_post_feed_request(self, mock_post_request: MagicMock,
                               mock_headers: MagicMock,
                               times: int,
                               expected_times: int):
        pet_name = "Egg-CottonCandyPink"
        food_name = "CottonCandyPink"

        feed_requester = FeedPostRequester(
            pet_name=pet_name, food_name=food_name, food_amount=times
        )

        _ = feed_requester.post_feed_request()

        expected_url = f"https://habitica.com/api/v3/user/feed/{pet_name}/{food_name}"
        mock_post_request.assert_called_with(
            url=expected_url,
            headers=mock_headers,
            params={"amount": expected_times},
            timeout=60
        )

    @pytest.mark.parametrize(
        "feed_plan_item", [
            FeedPlanItem(pet_name="Wolf-Ruby", food_name="Chocolate", times=4),
            FeedPlanItem(pet_name="TigerCub-Floral", food_name="Honey", times=2),
            FeedPlanItem(pet_name="Egg-Zombie", food_name="Meat", times=13),
            FeedPlanItem(pet_name="PandaCub-Shade", food_name="Milk", times=1)
        ]
    )
    def test_build_from_feed_plan_item(self, feed_plan_item: FeedPlanItem):
        requester: FeedPostRequester = FeedPostRequester.build_from(feed_plan_item)

        assert requester.pet_name == feed_plan_item.pet_name
        assert requester.food_name == feed_plan_item.food_name
        assert requester.query_params == {"amount": feed_plan_item.times}
