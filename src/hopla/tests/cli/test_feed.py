from hopla.cli.feed import PetFeedPostRequester


def test_petfeedpostrequester_path():
    pet = "Wolf-Golden"
    food = "Honey"

    feed_requester = PetFeedPostRequester(pet_name=pet,
                                          food_name=food)

    assert feed_requester.path == f"/user/feed/{pet}/{food}"
