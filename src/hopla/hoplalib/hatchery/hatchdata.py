#!/usr/bin/env python3
"""
Module with egg and hatch potion data.
"""
from typing import List


class EggData:
    """Class with data about eggs."""

    drop_egg_names = [
        "BearCub", "Cactus", "Dragon", "FlyingPig", "Fox", "LionCub",
        "PandaCub", "TigerCub", "Wolf"
    ]
    """
    Drop eggs. This is list was retrieved using: `hopla api content | jq .dropEggs | jq. keys`
    """

    quest_egg_names = [
        "Alligator", "Armadillo", "Axolotl", "Badger", "Beetle", "Bunny",
        "Butterfly", "Cheetah", "Cow", "Cuttlefish", "Deer", "Dolphin", "Egg",
        "Falcon", "Ferret", "Frog", "Gryphon", "GuineaPig", "Hedgehog",
        "Hippo", "Horse", "Kangaroo", "Monkey", "Nudibranch", "Octopus",
        "Owl", "Parrot", "Peacock", "Penguin", "Pterodactyl", "Rat", "Robot",
        "Rock", "Rooster", "Sabretooth", "SeaSerpent", "Seahorse", "Sheep",
        "Slime", "Sloth", "Snail", "Snake", "Spider", "Squirrel", "TRex",
        "Treeling", "Triceratops", "Turtle", "Unicorn", "Velociraptor",
        "Whale", "Yarn"
    ]
    """
    Quest Eggs. This is list was retrieved using: `hopla api content | jq .questEggs | jq keys`
    """

    egg_names: List[str] = drop_egg_names + quest_egg_names
    """All eggs in habitica."""


class HatchPotionData:
    """Class with data about hatching potions."""
    drop_hatch_potion_names = [
        "Base", "CottonCandyBlue", "CottonCandyPink", "Desert", "Golden",
        "Red", "Shade", "Skeleton", "White", "Zombie"
    ]
    """
    Drop hatching potions. This list was retrieved by using:
    hopla api content | jq.dropHatchingPotions | jq keys
    """

    magic_hatch_potion_names = [
        "Amber", "Aquatic", "Aurora", "AutumnLeaf", "BirchBark", "BlackPearl",
        "Bronze", "Celestial", "Cupid", "Ember", "Fairy", "Floral",
        "Fluorite", "Frost", "Ghost", "Glass", "Glow", "Holly", "IcySnow",
        "Moonglow", "MossyStone", "Peppermint", "PolkaDot", "Rainbow",
        "RoseQuartz", "RoyalPurple", "Ruby", "SandSculpture", "Shadow",
        "Shimmer", "Silver", "SolarSystem", "Spooky", "StainedGlass",
        "StarryNight", "Sunset", "Sunshine", "Thunderstorm", "Turquoise",
        "Vampire", "Watery", "Windup"
    ]
    """
    Magic hatching potions. This list was retrieved by using:
    hopla api content | jq .premiumHatchingPotions | jq keys
    """

    wacky_hatch_potion_names = ["Dessert", "Veggie"]
    """Wacky hatching potions. This list was retrieved by using:
           hopla api content | jq '.wackyHatchingPotions|keys'
    """
    non_drop_hatch_potion_names: List[str] = (
            magic_hatch_potion_names
            + wacky_hatch_potion_names
    )

    hatch_potion_names: List[str] = drop_hatch_potion_names + non_drop_hatch_potion_names
    """All potion names in habitica."""
