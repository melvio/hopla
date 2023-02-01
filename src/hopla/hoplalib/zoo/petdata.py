"""
A helper module with Pet Data.

Later on this module may be refactored to dynamically retrieve pet
data from the API. The retrieved data from the API can then be
cached locally. We then need to refresh our cache only when the
appVersion of the Habitica API increases. However, this approach
is overkill for now.
"""
from typing import List

from hopla.hoplalib.hatchery.egg_data import EggData
from hopla.hoplalib.hatchery.hatchpotion_data import HatchPotionData


def _combine_pets_and_pots(pets: List[str], pots: List[str]):
    return [pet + "-" + pot for pet in pets for pot in pots]


class PetData:
    """ Helper class with valid Habitica pets.

    For more info:
    * hopla api content | jq .petInfo
    * hopla api content | jq .mountInfo

    And also interesting:
    * hopla api content | jq .premiumPets
    * hopla api content | jq .pets
    * hopla api content | jq .questPets
    * hopla api content | jq .specialPets
    * hopla api content | jq .wackyPets
    """

    generation1_pet_names = _combine_pets_and_pots(
        pets=EggData.drop_egg_names,
        pots=HatchPotionData.drop_hatch_potion_names
    )
    """ https://habitica.fandom.com/wiki/Pets#Generation_1_Pets """

    # The Magic potion pets are known as "premium" by the API
    # <https://habitica.fandom.com/wiki/Pets#Magic_Potion_Pets>
    # hopla api content | jq '[.petInfo[] | select(.type=="premium")]'
    # hopla api content | jq '[.petInfo[] | select(.type=="premium") | .key]'
    magic_potion_pet_names = _combine_pets_and_pots(
        pets=EggData.drop_egg_names,
        pots=HatchPotionData.magic_hatch_potion_names
    )
    """Magic hatching pet names"""

    # Quest pets: @see:
    # <https://habitica.fandom.com/wiki/Pets#Quest_Pets>
    # <https://habitica.fandom.com/wiki/Pets#Magic_Potion_Pets>
    # hopla api content | jq '[.petInfo[] | select(.type=="quest")]'
    quest_pet_names = _combine_pets_and_pots(
        pets=EggData.quest_egg_names,
        pots=HatchPotionData.drop_hatch_potion_names
    )

    # hopla api content | jq '[.petInfo[] | select(.type=="wacky")]'
    wacky_pet_names = _combine_pets_and_pots(
        pets=EggData.drop_egg_names,
        pots=HatchPotionData.wacky_hatch_potion_names
    )

    world_boss_reward_pet_names = [
        "Hippogriff-Hopeful", "MagicalBee-Base", "Phoenix-Base", "Mammoth-Base",
        "MantisShrimp-Base"
    ]

    event_sequence_pet_names = [
        "Wolf-Veteran", "Turkey-Base", "JackOLantern-Base", "Tiger-Veteran", "Turkey-Gilded",
        "Lion-Veteran", "Gryphon-RoyalPurple", "JackOLantern-Ghost", "Orca-Base", "Bear-Veteran",
        "Fox-Veteran", "JackOLantern-Glow", "JackOLantern-RoyalPurple"
    ]
    """https://habitica.fandom.com/wiki/Event_Item_Sequences"""

    other_pet_names = [
        "Jackalope-RoyalPurple", "BearCub-Polar", "Dragon-Hydra", "Wolf-Cerberus",
        "Gryphatrice-Jubilant", "Gryphon-Gryphatrice", "Aether-Invisible"
    ]

    rare_pet_names = world_boss_reward_pet_names + event_sequence_pet_names + other_pet_names
    """Rare pet names are pets that cannot be hatched.
    @see: <https://habitica.fandom.com/wiki/Pets#Rare_Pets>
    """

    only_1favorite_food_pet_names = generation1_pet_names + quest_pet_names
    """Only quest pets and gen1 pets have only 1 favorite food (anno Sept. 2021)"""

    feedable_pet_names = only_1favorite_food_pet_names + magic_potion_pet_names
    """
    Pets that can be fed are the gen1 pets, quest pets, and magic potion pets. (anno Sept. 2021).
    """

    unfeedable_pet_names = rare_pet_names + wacky_pet_names
    """Only wacky pets and rare pets cannot be fed anno 2022."""

    pet_names = (generation1_pet_names
                 + magic_potion_pet_names
                 + quest_pet_names
                 + wacky_pet_names
                 + rare_pet_names)
    """ @see: hopla api content | jq '[.petInfo[] | .key]' """
