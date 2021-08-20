#!/usr/bin/env python3
import sys
import os
import subprocess
import logging

log = logging.getLogger()


def execute_subcmd():
    # log.debug(f"this_file: {sys.argv[0]}")  # pylint: disable=logging-fstring-interpolation)
    cmd_file = sys.argv[1]
    arguments = sys.argv[2:]
    # f strings are likely to be faster, rather than slower, so disable pylint warning
    log.debug(
        f"File to be executed {cmd_file}, arguments to be passed {arguments}")  # pylint: disable=logging-fstring-interpolation)
    # log.debug(f"sys.path={sys.path}")
    subprocess.run(args=sys.argv[1:])


if __name__ == "__main__":
    execute_subcmd()
