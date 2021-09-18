import pytest

from hopla.hoplalib.zoo.petmodels import FeedingStatus


class TestFeedingStatus:
    @pytest.mark.parametrize(
        "feeding_status,expected_percentage",
        [(-1, 100), (5, 10), (7, 14), (48, 96)]
    )
    def test_to_percentage_ok(self, feeding_status: int,
                              expected_percentage: int):
        feeding_status = FeedingStatus(feeding_status)

        result_percentage = feeding_status.to_percentage()

        assert result_percentage == expected_percentage

    @pytest.mark.parametrize(
        "start_status,expected_food_items", [
            (45, 1),
            (44, 2),
            (40, 2),
            (39, 3),
            (5, 9),
        ]
    )
    def test_required_food_items_to_become_mount_favorite(self,
                                                          start_status: int,
                                                          expected_food_items: int):
        feeding_status = FeedingStatus(start_status)

        is_favorite = True
        result = feeding_status.required_food_items_to_become_mount(is_favorite)

        assert result == expected_food_items

    @pytest.mark.parametrize(
        "start_status,expected_food_items", [
            (49, 1),
            (45, 3),
            (44, 3),
            (40, 5),
            (39, 6),
            (6, 22),
            (5, 23),
        ]
    )
    def test_required_food_items_to_become_mount_not_favorite(self,
                                                              start_status: int,
                                                              expected_food_items: int):
        feeding_status = FeedingStatus(start_status)

        is_favorite = False
        result = feeding_status.required_food_items_to_become_mount(is_favorite)

        assert result == expected_food_items


class TestFeedingStatusHash:
    _feeding_statuses = [
        FeedingStatus(-1), FeedingStatus(), FeedingStatus(5),
        FeedingStatus(20), FeedingStatus(35), FeedingStatus(49)
    ]

    @pytest.mark.parametrize(
        "feeding_status", _feeding_statuses
    )
    def test___hash__(self, feeding_status: FeedingStatus):
        # A minimal requirement for __hash__ is that if 2 FeedingStatus objects are
        # identical, they MUST have the same hash.
        assert hash(feeding_status) == hash(feeding_status)

    @pytest.mark.parametrize(
        "feeding_status,equal_feeding_status",
        list(zip(_feeding_statuses + [FeedingStatus()],
                 _feeding_statuses + [FeedingStatus(5)]))
    )
    def test___hash__(self,
                      feeding_status: FeedingStatus,
                      equal_feeding_status: FeedingStatus):
        # A minimal requirement for __hash__ if 2 FeedingStatus objects
        # are equal (__eq__) , they MUST have the same hash.
        assert hash(feeding_status) == hash(feeding_status)
