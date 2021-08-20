#!/usr/bin/env python3
import sys
import subprocess
import logging


def setup_logging() -> logging.Logger:
    """Setup python logging for the entire hopla project"""
    # https://docs.python.org/3.8/howto/logging.html#logging-basic-tutorial
    logging.basicConfig(
        format='[%(levelname)s][%(filename)s] %(asctime)s - %(message)s',
        level=logging.DEBUG,
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    return logging.getLogger(__name__)


if __name__ == "__main__":
    log = setup_logging()
    # log.debug(f"this_file: {sys.argv[0]}")  # pylint: disable=logging-fstring-interpolation)

    cmd_file = sys.argv[1]
    arguments = sys.argv[2:]
    # f strings are likely to be faster, rather than slower, so disable pylint warning
    log.debug(f"File to be executed {cmd_file}, arguments to be passed {arguments}")  # pylint: disable=logging-fstring-interpolation)
    # log.debug(f"sys.path={sys.path}")

    subprocess.run(args=sys.argv[1:])
