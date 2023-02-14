#!/usr/bin/env python3
"""
Module with hatching potion data.
"""
from typing import List


class HatchPotionData:
    """Class with data about hatching potions."""
    drop_hatch_potion_names = [
        "Base", "CottonCandyBlue", "CottonCandyPink", "Desert", "Golden",
        "Red", "Shade", "Skeleton", "White", "Zombie"
    ]
    """
    Drop hatching potions. Also known as 1st gen potions.
    This list was retrieved by using:
    hopla api content | jq .dropHatchingPotions | jq keys
    """

    magic_hatch_potion_names = [
        "Amber", "Aquatic", "Aurora", "AutumnLeaf",
        "BirchBark", "BlackPearl", "Bronze",
        "Celestial", "Cupid", "Ember",
        "Fairy", "Floral", "Fluorite", "Frost",
        "Ghost", "Glass", "Glow", "Holly",
        "IcySnow", "Moonglow", "MossyStone", "Onyx",
        "Peppermint", "PinkMarble", "PolkaDot", "Porcelain",
        "Rainbow", "RoseQuartz", "RoyalPurple", "Ruby",
        "SandSculpture", "Shadow", "Shimmer", "Silver", "SolarSystem",
        "Spooky", "StainedGlass", "StarryNight", "Sunset", "Sunshine",
        "Thunderstorm", "Turquoise", "Vampire", "Watery", "Windup"
    ]
    """
    Magic hatching potions. This list was retrieved by using:
    hopla api content | jq .premiumHatchingPotions | jq keys
    """

    wacky_hatch_potion_names = ["Dessert", "Veggie", "VirtualPet"]
    """
    Wacky hatching potions. This list was retrieved by using:
           hopla api content | jq '.wackyHatchingPotions|keys'
    """

    non_drop_hatch_potion_names: List[str] = (
            magic_hatch_potion_names
            + wacky_hatch_potion_names
    )

    hatch_potion_names: List[str] = drop_hatch_potion_names + non_drop_hatch_potion_names
    """All potion names in habitica."""
