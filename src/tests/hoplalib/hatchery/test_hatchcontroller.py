#!/usr/bin/env python3
import pytest

from hopla.hoplalib.hatchery.hatchcontroller import HatchRequester


class TestHatchRequester:
    @pytest.mark.parametrize("egg_name,potion_name", [
        ("Cheetah", "Base"),
        ("Ferret", "CottonCandyBlue"),
        ("Wolf", "Skeleton"),
        ("Fox", "Polkadot")
    ])
    def test_url(self, egg_name: str, potion_name: str):
        requester = HatchRequester(egg_name=egg_name, hatch_potion_name=potion_name)

        result_url: str = requester.url

        assert result_url.endswith(f"/user/hatch/{egg_name}/{potion_name}")
