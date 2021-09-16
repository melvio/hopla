#!/usr/bin/env python3
from hopla.hoplalib.zoo.petcontroller import FeedPostRequester


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
