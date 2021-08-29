from pathlib import Path
from hopla.cli.complete import Bash


def test_default_bash_config_file_is_bashrc():
    bash = Bash()
    assert bash.config_file == Path.home() / ".bashrc"


def test_bash_enablement_code_for_bashrc():
    bash = Bash()
    assert bash.get_enablement_code_for_bashrc() == \
           'eval "$(_HOPLA_COMPLETE=bash_source hopla)"'


def test_bash_has_autocomplete_cmd():
    bash = Bash()
    assert bash.get_generated_autocomplete_cmd() == \
           "_HOPLA_COMPLETE=bash_source hopla"


def test_bas_supports_enablement():
    bash = Bash()
    assert bash.supports_automatic_complete_enablement()
