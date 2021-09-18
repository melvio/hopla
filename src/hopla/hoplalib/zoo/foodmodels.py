"""
A helper module for feeding logic.
"""

import math
from hopla.hoplalib.clickhelper import PrintableException


class InvalidFeedingStatus(PrintableException):
    """Exception raised when a pet is invalid."""

    def __init__(self, msg: str, *, pet=None):
        super().__init__(msg)
        self.pet = pet


class FeedingStatus:
    """A class implementing feeding status logic for pets"""
    START_FEEDING_STATE = 5
    FULLY_FED_STATE = 50
    FAVORITE_INCREMENT = 5
    NON_FAVORITE_INCREMENT = 2

    def __init__(self, feeding_status: int = START_FEEDING_STATE):
        # every pet starts at 5
        # 50 would turn the pet into a mount
        # The feeding status of 0 is documented but never returned anno Sept 2021 to
        #  my understanding and according to a comment made by @Alys on github
        #  in 2020.
        invalid_status = (feeding_status < -1
                          or feeding_status in [0, 1, 2, 3, 4]
                          or feeding_status >= 50)
        if invalid_status:
            raise InvalidFeedingStatus(f"{feeding_status=} is invalid")

        self.__feeding_status = feeding_status

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.__feeding_status})"

    def __eq__(self, other):
        return isinstance(other, FeedingStatus) and int(other) == int(self)

    def __hash__(self):
        return hash(self.__feeding_status)

    def __int__(self) -> int:
        return self.__feeding_status

    def required_food_items_to_become_mount(self, is_favorite_food: bool) -> int:
        """Return how many items of food we need to give to turn a pet into a mount."""
        target = FeedingStatus.FULLY_FED_STATE - self.__feeding_status
        if is_favorite_food:
            required_food = math.ceil(target / FeedingStatus.FAVORITE_INCREMENT)
        else:
            required_food = math.ceil(target / FeedingStatus.NON_FAVORITE_INCREMENT)
        return required_food

    def to_percentage(self) -> int:
        """
        Turn feeding status into percentage understandable by the
        website user.
        <https://habitica.fandom.com/wiki/Food_Preferences>
        """
        if self.__feeding_status == -1:
            return 100  # The pet is now a mount
        return self.__feeding_status * 2
