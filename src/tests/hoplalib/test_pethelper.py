#!/usr/bin/env python3
import pytest

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.pethelper import Pet, InvalidPet


class TestPetInit:
    def test_init_raises_invalid_pet_name(self):
        with pytest.raises(InvalidPet) as execinfo:
            invalid_pet_name = "INVALID_PET"
            Pet(invalid_pet_name)

        err_msg = str(execinfo.value)
        assert invalid_pet_name in err_msg
        assert f"an issue at {GlobalConstants.NEW_ISSUE_URL}" in err_msg

    def test_init_raises_invalid_feeding_status(self):
        with pytest.raises(InvalidPet) as execinfo:
            invalid_feed_status = 4
            Pet("PandaCub-IcySnow", feeding_status=invalid_feed_status)

        err_msg = str(execinfo.value)
        assert f"feeding_status={invalid_feed_status}" in err_msg
