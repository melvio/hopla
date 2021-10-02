#!/usr/bin/env python3
import logging
import re
from re import Pattern

import pytest
from click.testing import CliRunner, Result

from hopla import hopla
from hopla.cli.version import version
from hopla.kickstart import setup_logging


class TestVersionCliCommand:
    def test_version(self, semver_pattern: Pattern):
        runner = CliRunner()
        result: Result = runner.invoke(version)

        assert re.fullmatch(pattern=semver_pattern, string=result.stdout)
        assert result.exit_code == 0

    def test_version_similar_to_hopla_version_option(self, semver_pattern: Pattern):
        runner = CliRunner()
        result_cmd: Result = runner.invoke(version)
        result_option: Result = runner.invoke(hopla, ["--version"])

        # hopla --version prefixes 'hopla, version'
        assert result_option.stdout == f"hopla, version {result_cmd.stdout}"

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
            "\n"  # added the \n here
        )


class TestHoplaCommand:
    def test_hopla_base_cmd_gives_help(self):
        runner = CliRunner()
        result_hopla: Result = runner.invoke(hopla)
        result_h: Result = runner.invoke(hopla, ["-h"])
        result_help: Result = runner.invoke(hopla, ["--help"])

        assert result_hopla.exit_code == 0
        assert result_help.exit_code == 0
        assert result_hopla.stdout == result_help.stdout
        assert result_h.stdout == result_help.stdout


class TestSetupLogging:
    def test_setup_logging(self):
        result_logger: logging.Logger = setup_logging()

        assert result_logger.name == "hopla"
