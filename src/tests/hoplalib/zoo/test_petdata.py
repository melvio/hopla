#!/usr/bin/env python3
import random

import pytest

from hopla.hoplalib.zoo.petdata import PetData

_SAMPLE_SIZE_LARGE = 20
_SAMPLE_SIZE_SMALL = 5


class TestPetData:

    @pytest.mark.parametrize(
        "gen1pet,magic_pet,quest_pet", list(zip(
            random.sample(PetData.generation1_pet_names, k=_SAMPLE_SIZE_LARGE),
            random.sample(PetData.magic_potion_pet_names, k=_SAMPLE_SIZE_LARGE),
            random.sample(PetData.quest_pet_names, k=_SAMPLE_SIZE_LARGE)
        ))
    )
    def test_correct_grouping_of_feedable_pets(self, gen1pet: str,
                                               magic_pet: str,
                                               quest_pet: str):
        assert gen1pet not in PetData.magic_potion_pet_names
        assert gen1pet not in PetData.quest_pet_names
        assert magic_pet not in PetData.generation1_pet_names
        assert magic_pet not in PetData.quest_pet_names
        assert quest_pet not in PetData.generation1_pet_names
        assert quest_pet not in PetData.magic_potion_pet_names

        assert gen1pet in PetData.feedable_pet_names
        assert magic_pet in PetData.feedable_pet_names
        assert quest_pet in PetData.feedable_pet_names

        assert gen1pet in PetData.only_1favorite_food_pet_names
        assert magic_pet not in PetData.only_1favorite_food_pet_names
        assert quest_pet in PetData.only_1favorite_food_pet_names

        assert gen1pet not in PetData.unfeedable_pet_names
        assert magic_pet not in PetData.unfeedable_pet_names
        assert quest_pet not in PetData.unfeedable_pet_names

        assert gen1pet in PetData.pet_names
        assert magic_pet in PetData.pet_names
        assert quest_pet in PetData.pet_names

    @pytest.mark.parametrize(
        "wacky_pet,world_boss_pet,event_sequence_pet,other_pet", list(zip(
            random.sample(PetData.wacky_pet_names, k=_SAMPLE_SIZE_SMALL),
            random.sample(PetData.world_boss_reward_pet_names, k=_SAMPLE_SIZE_SMALL),
            random.sample(PetData.event_sequence_pet_names, k=_SAMPLE_SIZE_SMALL),
            random.sample(PetData.other_pet_names, k=_SAMPLE_SIZE_SMALL),
        ))
    )
    def test_correct_grouping_rare_pets(self,
                                        wacky_pet: str,
                                        world_boss_pet: str,
                                        event_sequence_pet: str,
                                        other_pet: str):
        assert wacky_pet not in PetData.world_boss_reward_pet_names
        assert wacky_pet not in PetData.event_sequence_pet_names
        assert wacky_pet not in PetData.other_pet_names

        assert world_boss_pet not in PetData.wacky_pet_names
        assert world_boss_pet not in PetData.event_sequence_pet_names
        assert world_boss_pet not in PetData.other_pet_names

        assert event_sequence_pet not in PetData.wacky_pet_names
        assert event_sequence_pet not in PetData.world_boss_reward_pet_names
        assert event_sequence_pet not in PetData.other_pet_names

        assert other_pet not in PetData.wacky_pet_names
        assert other_pet not in PetData.event_sequence_pet_names
        assert other_pet not in PetData.world_boss_reward_pet_names

        assert wacky_pet in PetData.unfeedable_pet_names
        assert world_boss_pet in PetData.unfeedable_pet_names
        assert event_sequence_pet in PetData.unfeedable_pet_names
        assert other_pet in PetData.unfeedable_pet_names

        assert wacky_pet not in PetData.only_1favorite_food_pet_names
        assert world_boss_pet not in PetData.only_1favorite_food_pet_names
        assert event_sequence_pet not in PetData.only_1favorite_food_pet_names
        assert other_pet not in PetData.only_1favorite_food_pet_names

        assert wacky_pet not in PetData.feedable_pet_names
        assert world_boss_pet not in PetData.feedable_pet_names
        assert event_sequence_pet not in PetData.feedable_pet_names
        assert other_pet not in PetData.feedable_pet_names

        assert wacky_pet not in PetData.rare_pet_names
        assert world_boss_pet in PetData.rare_pet_names
        assert event_sequence_pet in PetData.rare_pet_names
        assert other_pet in PetData.rare_pet_names
