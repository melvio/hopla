#!/usr/bin/env python3
import pytest

from hopla.hoplalib.cast.spellmodel import Spell, SpellData
from hopla.hoplalib.errors import YouFoundABugRewardError


class TestSpellData:

    def test_spell_values_in_single_arg_spells(self):
        assert all(spell in SpellData.single_arg_spells
                   for spell in SpellData.warrior_spells_single_arg)
        assert all(spell in SpellData.single_arg_spells
                   for spell in SpellData.mage_spells_single_arg)
        assert all(spell in SpellData.single_arg_spells
                   for spell in SpellData.healer_spells_single_arg)
        assert all(spell in SpellData.single_arg_spells
                   for spell in SpellData.rogue_spells_single_arg)


class TestSpell:
    def test_class_name_ok(self):
        assert Spell("mpheal").class_name == "mage"
        assert Spell("heal").class_name == "healer"
        assert Spell("stealth").class_name == "rogue"
        assert Spell("intimidate").class_name == "warrior"

    @pytest.mark.parametrize("spell_name", SpellData.single_arg_spells)
    def test__init__ok(self, spell_name: str):
        spell = Spell(spell_name=spell_name)
        assert spell.spell_name == spell_name
        assert spell.target_id is None  # not supported for now

    def test__init__fail(self):
        invalid_spell_name = "cureAllDisease"
        with pytest.raises(YouFoundABugRewardError) as execinfo:
            Spell(invalid_spell_name)

        msg = str(execinfo.value)
        assert f"'{invalid_spell_name}' does not exist" in msg
