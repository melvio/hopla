#!/usr/bin/env python3
import pytest
import random

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.pethelper import Pet, InvalidPet, FeedingData


class TestPetInit:
    def test_init_raises_invalid_pet_name(self):
        with pytest.raises(InvalidPet) as execinfo:
            invalid_pet_name = "INVALID_PET"
            Pet(invalid_pet_name)

        err_msg = str(execinfo.value)
        assert invalid_pet_name in err_msg
        assert f"an issue at {GlobalConstants.NEW_ISSUE_URL}" in err_msg

    @pytest.mark.parametrize(
        "pet_name",
        # Testing all pets takes too long (approx. 2 seconds) so sample.
        random.sample(FeedingData.pet_names, k=50))
    def test_init_valid_pet_name(self, pet_name: str):
        pet = Pet(pet_name=pet_name)
        assert pet.pet_name == pet_name

    @pytest.mark.parametrize(
        "invalid_feed_status",
        [-10, -2, 1, 3, 51, 100]
    )
    def test_init_raises_invalid_feeding_status(self, invalid_feed_status: int):
        with pytest.raises(InvalidPet) as execinfo:
            Pet("PandaCub-IcySnow", feeding_status=invalid_feed_status)

        print(invalid_feed_status)
        err_msg = str(execinfo.value)
        assert f"feeding_status={invalid_feed_status}" in err_msg
