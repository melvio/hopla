#!/usr/bin/env python3
from hopla.cli.groupcmds.get_user import HabiticaUser


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
