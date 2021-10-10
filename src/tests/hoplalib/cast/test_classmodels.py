#!/usr/bin/env python3
from typing import List


class HabiticaClassData:
    """A class with data about habitica classes.

    @see: hopla api content | jq .classes
    """
    class_names: List[str] = ["warrior", "rogue", "healer", "wizard"]
