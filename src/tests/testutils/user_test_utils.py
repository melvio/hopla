#!/usr/bin/env python3
"""TestUtils to get HabiticaUser objects for users."""
from typing import Dict, Optional

from hopla.cli.groupcmds.get_user import HabiticaUser


class UserTestUtil:
    """test utility to create an user"""

    @classmethod
    def user_with_zoo(cls, *,
                      pets: Optional[Dict[str, int]] = None,
                      mounts: Optional[Dict[str, bool]] = None) -> HabiticaUser:
        """Create a simple user to test pet and mount logic"""
        if pets is None:
            pets = {}
        if mounts is None:
            mounts = {}

        return HabiticaUser({"items": {"pets": pets, "mounts": mounts}})

    @classmethod
    def user_with_gp(cls, *,
                     gold: float):
        """Create the simplest user with the specified budget."""
        return HabiticaUser({"stats": {"gp": gold}})
