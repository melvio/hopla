#!/usr/bin/env python3
import pytest

from hopla.hoplalib.dict_filters import JqFilter


class TestJqFilter:

    def test_jqfilter_init_none_is_identity(self):
        compiled_jq_filter = JqFilter(jq_filter_spec=None).compiled_jq_filter
        assert compiled_jq_filter.program_string == "."

    def test_jqfilter_valid_filter(self):
        valid_filter: str = ".data | add"
        jq_filter_compiled = JqFilter(jq_filter_spec=valid_filter).compiled_jq_filter
        assert jq_filter_compiled.program_string == valid_filter

    def test_jqfilter_init_exits_on_invalid_jqfilterstr(self):
        invalid_filter: str = " \\o// | //o\\ "
        with pytest.raises(SystemExit) as execinfo:
            JqFilter(jq_filter_spec=invalid_filter)

        assert "Exiting: Please provide a different compile string" in str(execinfo.value)
