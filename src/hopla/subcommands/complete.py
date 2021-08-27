import click
import subprocess
import os
from pathlib import Path
import abc

import logging

log = logging.getLogger()


# def get_user_specific_bash_completion_dir() -> Path:
#     """"return the user specific bash-completion dir
#     Get completion dir in order of precedence:
#     1. $BASH_COMPLETION_USER_DIR/completions or if $BASH_COMPLETION_USER_DIR doesnt exit
#     2. $XDG_DATA_HOME/bash-completion or if $XDG_DATA_HOME does not exist
#     3. ~/.local/share/bash-completion
#     """
#     bash_completion_user_dir = os.environ.get("BASH_COMPLETION_USER_DIR")
#     xdg_data_home = os.environ.get("XDG_DATA_HOME")
#     if bash_completion_user_dir is not None:
#         return Path(bash_completion_user_dir) / "completions"
#     elif xdg_data_home is not None:
#         return Path(xdg_data_home) / "bash-completion"
#     else:
#         return Path.home() / ".local" / "share" / "bash-completion"

class RecognizedShell(abc.ABC):
    def __init__(self, shell_name: str):
        self.shell_name = shell_name

    def __str__(self):
        return self.__class__.__name__ + "(" + f"shell_name={self.shell_name}" + ")"

    @abc.abstractmethod
    def get_generated_autocomplete_cmd(self) -> str:
        """Returns the command needed to generate autocomplete code"""
        pass

    @abc.abstractmethod
    def get_enable_autocomplete_config_code(self) -> str:
        """
        Returns the code to be added to the shell config file to enable autocompletion automatically
        """
        pass


class Bash(RecognizedShell):
    def __init__(self):
        super().__init__("bash")

    def get_generated_autocomplete_cmd(self) -> str:
        return f"_HOPLA_COMPLETE={self.shell_name}_source hopla"

    def get_enable_autocomplete_config_code(self) -> str:
        cmd = self.get_generated_autocomplete_cmd()
        return f'eval "$({cmd})"'


class Zsh(RecognizedShell):
    def __init__(self):
        super().__init__("zsh")

    def get_generated_autocomplete_cmd(self) -> str:
        return f"_HOPLA_COMPLETE={self.shell_name}_source hopla"

    def get_enable_autocomplete_config_code(self) -> str:
        raise NotImplementedError(f"not available for {self.shell_name}")


class Fish(RecognizedShell):
    def __init__(self):
        super().__init__("fish")

    def get_generated_autocomplete_cmd(self) -> str:
        return f"env _HOPLA_COMPLETE={self.shell_name}_source hopla"

    def get_enable_autocomplete_config_code(self) -> str:
        raise NotImplementedError(f"not available for {self.shell_name}")


def get_generated_autocomplete_cmd(shell_name: str):
    if shell_name == "bash" or shell_name == "zsh":
        return f"_HOPLA_COMPLETE={shell_name}_source hopla"
    elif shell_name == "fish":
        return f"env _HOPLA_COMPLETE={shell_name}_source hopla"
    else:
        # Should not be raised to CLI-user
        raise ValueError(f"shell {shell_name} not supported")


def get_generated_autocomplete_sourced(shell_name: str):
    if shell_name == "bash":
        cmd = get_generated_autocomplete_cmd(shell_name)
        return f'eval "$({cmd})"'
    else:
        # Should not be raised to CLI-user
        raise ValueError(f"shell {shell_name} not supported")


autocomplete_supported_shells = click.Choice(["bash", "zsh", "fish"])


@click.command()
@click.argument("shell", type=autocomplete_supported_shells, default="bash")
# @click.option("--show-completion", is_flag=True, default=True, show_default=True)
@click.option("--enable-automatically", is_flag=True, default=False, show_default=True)
def complete(shell: str, enable_automatically: bool):
    """print (and optionally enable) shell autocompletion

    \f
    :param shell:
    :param enable_automatically:
    :return:
    """
    log.debug(f"hopla complete {shell} --enable-automatically={enable_automatically}")

    if enable_automatically is False:
        cmd_str = get_generated_autocomplete_cmd(shell)
        os.system(cmd_str)
    else:
        if shell == "bash":
            cmd_str = get_generated_autocomplete_sourced(shell)
            click.echo(cmd_str)
        else:
            click.echo(f"Sorry, automatic installation is not supported for {shell}.")
            click.echo(f"You can enable autocompletion manually by running:")
            if shell == "fish":
                click.echo(f"   hopla autocomplete {shell} > ~/.config/fish/completions/hopla.fish")
            elif shell == "zsh":
                example_zsh_complete_file = "~/hopla-zsh-completion.zsh"
                click.echo(f"   hopla autocomplete {shell} > {example_zsh_complete_file}")
                click.echo(f"Then source the file in your ~/.zshrc:")
                click.echo(f"   . {example_zsh_complete_file}")
