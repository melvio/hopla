#!/usr/bin/env python3
import pytest

from hopla.hoplalib.cast.castcontroller import PostCastRequest
from hopla.hoplalib.cast.spellmodel import Spell, SpellData


class TestPostCastRequest:
    @pytest.mark.parametrize("spell_name", SpellData.single_arg_spells)
    def test_url_ok(self, spell_name: str):
        cast_request = PostCastRequest(spell=Spell(spell_name))

        url_result: str = cast_request.url

        assert url_result == f"https://habitica.com/api/v3/user/class/cast/{spell_name}"
