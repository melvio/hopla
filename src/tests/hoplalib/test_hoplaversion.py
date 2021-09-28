#!/usr/bin/env python3
import re
from re import Pattern
from typing import Optional

import pytest

from hopla.hoplalib.hoplaversion import HoplaVersion


class TestHoplaVersion:

    def test_semantic_version_defaults(self, semver_pattern: Pattern):
        hopla_version = HoplaVersion()
        result: str = hopla_version.semantic_version()
        assert re.fullmatch(pattern=semver_pattern, string=result)

    @pytest.mark.parametrize("prerelease_value", [None, ""])
    def test_semantic_version_without_prerelease(self, semver_pattern: Pattern,
                                                 prerelease_value: Optional[str]):
        hopla_version = HoplaVersion(pre_release=prerelease_value)
        result: str = hopla_version.semantic_version()
        assert re.fullmatch(pattern=semver_pattern, string=result)

    def test_semantic_version_ok(self, semver_pattern: Pattern):
        hopla_version = HoplaVersion(major_version=123,
                                     minor_version=200,
                                     patch_version=69,
                                     pre_release="beta")

        result: str = hopla_version.semantic_version()
        assert result == "123.200.69-beta"
        assert re.fullmatch(pattern=semver_pattern, string=result)

    @pytest.fixture
    def semver_pattern(self) -> Pattern:
        """Regex adopted from <https://semver.org/>"""
        return re.compile(
            r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
            r"(?:-("
            r"?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
            r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*"
            r"))?"
            r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
        )
