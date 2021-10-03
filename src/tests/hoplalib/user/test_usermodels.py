#!/usr/bin/env python3
from hopla.hoplalib.user.usermodels import HabiticaUser


class TestHabiticaUser:

    def test_get_stats(self):
        user_test_stat_values = {
            "buffs": {
                "str": 50, "int": 50, "per": 3206, "con": 50, "stealth": 0, "streaks": False,
                "snowball": False, "spookySparkles": False, "shinySeed": False, "seafoam": False
            },
            "training": {"int": 0, "per": 0, "str": 0, "con": 0},
            "hp": 50, "mp": 65.7, "exp": 2501, "gp": 1072327.9, "lvl": 121,
            "class": "wizard", "points": 0, "str": 0, "con": 0, "int": 12, "per": 88,
            "toNextLevel": 5010, "maxHealth": 50, "maxMP": 304
        }

        user = HabiticaUser(user_dict={"stats": user_test_stat_values})

        assert user.get_stats() == user_test_stat_values

    def test_get_auth(self):
        user_test_auth_values = {
            "local": {"username": "hopla", "lowerCaseUsername": "hopla",
                      "email": "something+habitica@gmail.com"
                      },
            "timestamps": {"created": "2022-03-22T24:23:38.119Z",
                           "loggedin": "2022-09-18T08:47:45.286Z",
                           "updated": "2022-09-18T14:20:55.530Z"
                           },
            "facebook": {}, "google": {}, "apple": {}
        }

        user = HabiticaUser(user_dict={"auth": user_test_auth_values})

        assert user.get_auth() == user_test_auth_values

    def test_get_inventory(self):
        inventory = {
            "gear": {"equipped": {"back": "back_special_aetherCloak"},
                     "costume": {"armor": "armor_armoire_bluePartyDress", "body": "body_base_0"},
                     "owned": {"armor_special_fall2019Healer": True}},
            "special": {"goodluck": 9000},
            "lastDrop": {"count": 80, "date": "2021-10-12T15:45:30.384Z"},
            "pets": {"Cactus-Golden": 0, "Unicorn-Red": -1, "Wolf-CottonCandyPink": 5},
            "eggs": {"Dragon": 338, "Nudibranch": 3, "TRex": 0},
            "hatchingPotions": {"Desert": 456, "MossyStone": 1},
            "food": {"RottenMeat": 846},
            "mounts": {"Fox-RoyalPurple": True, "Dragon-Skeleton": None, "Wolf-MossyStone": True},
            "quests": {"trex_undead": 0},
            "currentPet": "Egg-Base",
            "currentMount": "Aether-Invisible"
        }
        user = HabiticaUser(user_dict={"items": inventory})
        assert user.get_inventory() == inventory

    def test_get_gp(self):
        gp = 12.0
        user = HabiticaUser(user_dict={"stats": {"gp": gp}})
        assert user.get_gp() == gp

    def test_get_mp(self):
        mp = 112.0
        user = HabiticaUser(user_dict={"stats": {"mp": mp}})
        assert user.get_mp() == mp

    def test_get_pets(self):
        pets = {"Spider-Base": -1, "TRex-Skeleton": 5}
        user = HabiticaUser(user_dict={"items": {"pets": pets}})
        assert user.get_pets() == pets

    def test_get_mounts(self):
        mounts = {"Spider-Base": None, "TRex-Skeleton": True}
        user = HabiticaUser(user_dict={"items": {"mounts": mounts}})
        assert user.get_mounts() == mounts

    def test_get_food(self):
        food = {"CottonCandyBlue": 10, "Fish": 830}
        user = HabiticaUser(user_dict={"items": {"food": food}})
        assert user.get_food() == food

    def test_get_hatch_potions(self):
        hatch_potions = {"Base": 10, "SolarSystem": 1009}
        user = HabiticaUser(user_dict={"items": {"hatchingPotions": hatch_potions}})
        assert user.get_hatch_potions() == hatch_potions

    def test_get_eggs(self):
        eggs = {"Fox": 1001, "Nudibranch": 9}
        user = HabiticaUser(user_dict={"items": {"eggs": eggs}})
        assert user.get_eggs() == eggs
