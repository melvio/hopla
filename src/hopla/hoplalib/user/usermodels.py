#!/usr/bin/env python3
"""
Module with models for a Habitica user.
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class HabiticaUser:
    """
    Class representing a habitica user.
    """
    # pylint: disable=too-many-public-methods
    #################################################################
    # In a way, pylint is right. This class does have a lot of functions.
    # Most of these are oneliners, however we can also create
    # UserInventory, UserStats, etc object to compose this class from.
    # We can also use an extension (e.g. HoplaUser) which isA HabiticaUser
    # but where we add 'extra' functionality such as get_gems.
    # However, that is really overkill for now, and really urgent.
    # Therefore, too-many-public-methods is disabled for this class.
    #################################################################

    user_dict: dict
    """
    The user_dict is assumed to be returned from a 200 ok requests.Response
    (and using Response.json()) when calling the /user endpoint and getting
    "data" from the json.
    """

    def __getitem__(self, key):
        return self.user_dict.__getitem__(key)

    def get_stats(self) -> dict:
        """Index the user_dict for 'stats' and return the result"""
        return self["stats"]

    def get_gp(self) -> float:
        """Get the gold of a user."""
        return self.get_stats()["gp"]

    def get_mp(self) -> float:
        """Get the mana of a user."""
        return self.get_stats()["mp"]

    def get_hp(self) -> float:
        """Get the health of a user."""
        return self.get_stats()["hp"]

    def get_inventory(self) -> dict:
        """Index the user_dict for 'items' and return the result"""
        return self["items"]

    def get_pets(self) -> Dict[str, int]:
        """Return the pets of a user.

        :return: A dictionary with pet_name as key and feed_status as value.
        For example: {"Spider-Base": -1, "TRex-Skeleton": 5}
        """
        return self.get_inventory()["pets"]

    def get_eggs(self) -> Dict[str, int]:
        """Return the eggs of a user.

        :return: A dictionary with egg_names as keys and amount as values.
        For example: { "Dragon": 338, "Octopus": 0}
        """
        return self.get_inventory()["eggs"]

    def get_hatch_potions(self) -> Dict[str, int]:
        """Return the hatching potions of a user.

        :return: A dict with hatch_potion_names as keys and amount as value.
        For example: { "Desert": 456, "Glow": 0}
        """
        return self.get_inventory()["hatchingPotions"]

    def get_mounts(self) -> Dict[str, Optional[bool]]:
        """Return the mounts of a user.

        :return: A dictionary with mount_name as key and availability as value.
        For example: { "Dragon-Base": None, "Octopus-Shade": True }
        """
        return self.get_inventory()["mounts"]

    def get_food(self) -> Dict[str, int]:
        """Return the food that the user has"""
        return self.get_inventory()["food"]

    def get_auth(self) -> dict:
        """Index the user_dict for 'auth' and return the result"""
        return self["auth"]

    def get_gems(self) -> int:
        """Get the number of gems of a user.

        gems are stored in the 'balance' field. 1 'balance' equals 4 gems
        [see](https://habitica.fandom.com/wiki/Gems#Information_for_Developers)
        """
        balance = self["balance"]
        return int(balance * 4)
