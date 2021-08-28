import abc
import logging
import os
from pathlib import Path

import click

log = logging.getLogger()


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
    def supports_automatic_complete_enablement(self) -> bool:
        """Returns whether this shell supports automatic enablement of autocomplete """
        pass

    @abc.abstractmethod
    def handle_enable_complete_request(self):
        """"Handle request for enabling autocomplete regardless if there is support for it"""
        pass


class RecognizedShellWithAutomaticAutocompleteDisabled(RecognizedShell, abc.ABC):
    def __init__(self, shell_name: str):
        super().__init__(shell_name)

    @abc.abstractmethod
    def get_manual_autocomplete_instructions(self) -> [str]:
        """Returns instructions on how the enable hopla autocompletion for this shell"""
        pass

    def handle_enable_complete_request(self) -> [str]:
        return self.get_manual_autocomplete_instructions()

    def supports_automatic_complete_enablement(self) -> bool:
        return False


class RecognizedShellWithAutomaticAutocompleteEnabled(RecognizedShell, abc.ABC):
    def __init__(self, shell_name: str):
        super().__init__(shell_name)

    @abc.abstractmethod
    def enable_autocomplete(self) -> None:
        """Enables hopla autocompletion"""
        pass

    def handle_enable_complete_request(self) -> None:
        self.enable_autocomplete()

    def supports_automatic_complete_enablement(self) -> bool:
        return True


class Bash(RecognizedShellWithAutomaticAutocompleteEnabled):

    def __init__(self):
        super().__init__("bash")
        self.config_file: Path = Path.home() / ".bashrc"

    def get_generated_autocomplete_cmd(self) -> str:
        return f"_HOPLA_COMPLETE={self.shell_name}_source hopla"

    def enable_autocomplete(self):
        cmd = self.get_generated_autocomplete_cmd()
        enablement_code_for_bashrc = f'eval "$({cmd})"'
        with open(self.config_file, "a") as f:
            f.write(enablement_code_for_bashrc)


class Zsh(RecognizedShellWithAutomaticAutocompleteDisabled):
    def __init__(self):
        super().__init__("zsh")
        self.example_zsh_complete_file: str = "~/hopla-zsh-completion.zsh"
        self.config_file: str = "~/.zshrc"

    def get_generated_autocomplete_cmd(self) -> str:
        return f"_HOPLA_COMPLETE={self.shell_name}_source hopla"

    def get_manual_autocomplete_instructions(self) -> [str]:
        return [f"   hopla autocomplete {self.shell_name} > {self.example_zsh_complete_file}",
                f"Then source the file in your {self.config_file}",
                f"   . {self.example_zsh_complete_file}"]


class Fish(RecognizedShellWithAutomaticAutocompleteDisabled):
    def __init__(self):
        super().__init__("fish")
        self.hopla_complete_file = "~/.config/fish/completions/hopla.fish"

    def get_generated_autocomplete_cmd(self) -> str:
        return f"env _HOPLA_COMPLETE={self.shell_name}_source hopla"

    def get_manual_autocomplete_instructions(self) -> [str]:
        return [f"   hopla autocomplete {self.shell_name} > {self.hopla_complete_file}"]


supported_shell_mapping = {"bash": Bash, "zsh": Zsh, "fish": Fish}


def get_shell_by_name(shell_name: str) -> RecognizedShell:
    """Get a shell by its name"""
    shell_class = supported_shell_mapping.get(shell_name)
    if shell_class is not None:
        return shell_class()
    else:
        # defensive programming: should be handled by click.Choice already
        raise ValueError(f"Unexpected shell {shell_name}")


autocomplete_supported_shells = click.Choice(list(supported_shell_mapping.keys()))


@click.command()
@click.argument("shell", type=autocomplete_supported_shells, default="bash")
@click.option("--enable", is_flag=True, default=False,
              help="Automatically add hopla autocompletion to your shell's config")
def complete(shell: str, enable: bool):
    """print or enable shell autocompletion

    \b
    Examples
    ---
    # automatically add autocompletion for bash (bash is used when no shell is provided)
    hopla complete --enable

    \b
    # show the autocomplete code for zsh
    hopla complete zsh


    \f
    :param shell:
    :param enable:
    :return:
    """
    log.debug(f"hopla complete {shell} --enable={enable}")

    shell_obj: RecognizedShell = get_shell_by_name(shell_name=shell)

    if enable is False:
        show_autocomplete_code(shell_obj)
    else:
        # TODO: check if it is already enabled, if it is then abort in friendly manner
        if shell_obj.supports_automatic_complete_enablement():
            enable_autocomplete(shell_obj)
        else:
            show_manual_autocomplete_code(shell_obj)


def show_manual_autocomplete_code(shell_obj: RecognizedShell):
    click.echo(f"Sorry, automatic installation is not supported for {shell_obj.shell_name}.")
    click.echo(f"You can enable autocompletion manually by running:")
    instructions: [str] = shell_obj.handle_enable_complete_request()
    for instruction in instructions:
        click.echo(instruction)


def enable_autocomplete(shell_obj):
    shell_obj.handle_enable_complete_request()
    click.echo("enabled autocompletion")
    click.echo(f"restart {shell_obj.shell_name} to make use of it")


def show_autocomplete_code(shell_obj):
    cmd_str = shell_obj.get_generated_autocomplete_cmd()
    os.system(cmd_str)
