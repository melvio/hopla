#!/usr/bin/env python3
"""
Module with egg and hatch potion data.
"""
from typing import List


class EggData:
    """Class with data about eggs."""

    drop_egg_names: List[str] = [
        "BearCub", "Cactus", "Dragon", "FlyingPig", "Fox", "LionCub",
        "PandaCub", "TigerCub", "Wolf"
    ]
    """
    Drop eggs. This is list was retrieved using: `hopla api content | jq .dropEggs | jq. keys`
    """

    quest_egg_names: List[str] = [
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
    Quest Eggs. This is list was retrieved using:
    hopla api content | jq .questEggs | jq keys
    """

    egg_names: List[str] = drop_egg_names + quest_egg_names
    """All eggs in habitica."""
