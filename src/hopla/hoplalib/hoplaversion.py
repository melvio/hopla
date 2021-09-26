#!/usr/bin/env python3
"""
Module with hopla versioning logic.
"""
from dataclasses import dataclass
from typing import Optional

MAJOR_VERSION: int = 0
MINOR_VERSION: int = 0
PATCH_VERSION: int = 16
PRE_RELEASE: Optional[str] = "alpha"


@dataclass
class HoplaVersion:
    """Class with HoplaVersion constants."""

    def __init__(self,
                 major_version=MAJOR_VERSION,
                 minor_version=MINOR_VERSION,
                 patch_version=PATCH_VERSION,
                 pre_release: Optional[str] = PRE_RELEASE):
        self.major_version = major_version
        self.minor_version = minor_version
        self.patch_version = patch_version
        self.pre_release: str = pre_release or ""

    def full_version(self) -> str:
        """
        Returns the hopla version (Not to be confused with the habitica API version)

        The output satisfies [semantic versioning](https://semver.org/)
        :return:
        """

        version_core = f"{self.major_version}.{self.minor_version}.{self.patch_version}"
        sep = "-" if self.pre_release != "" else ""

        return f"{version_core}{sep}{self.pre_release}"
