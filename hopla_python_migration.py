#!/usr/bin/env python3

import sys
import subprocess
import os
from pathlib import Path


def execute_hopla_dot_shell():
    script_dirname = os.path.dirname(Path(__file__).resolve())
    cmd_entry = script_dirname + "/hopla.sh"
    hopla_env = create_hopla_env(script_dirname)
    subprocess.run([cmd_entry] + sys.argv[1:], env=hopla_env)


def create_hopla_env(script_dirname):
    library_dir = script_dirname + "/library"
    hopla_env = os.environ
    hopla_env["script_dirname"] = script_dirname
    hopla_env["library_dir"] = library_dir
    return hopla_env


if __name__ == "__main__":
    execute_hopla_dot_shell()
