#!/usr/bin/env python3
import sys
import subprocess
import logging


def setup_logging() -> logging.Logger:
    """Setup python logging for the entire hopla project"""
    logging.basicConfig(
        format='[%(levelname)s][%(filename)s] %(asctime)s - %(message)s',
        level=logging.DEBUG,
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    return logging.getLogger(__name__)


if __name__ == "__main__":
    # https://docs.python.org/3.8/howto/logging.html#logging-basic-tutorial
    log = setup_logging()

    cmd_file = sys.argv[1]
    arguments = sys.argv[2:]
    log.debug(f"File to be executed {cmd_file}, arguments to be passed {arguments}")  # pylint: disable=logging-fstring-interpolation)
    # log.debug(f"sys.path={sys.path}")

    subprocess.call(args=sys.argv[1:])
