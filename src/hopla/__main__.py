#!/usr/bin/env python3
"""
The __main__.py module allows hopla to be ran as python -m hopla.
Moreover, it is used by setup.cfg to construct hopla as a console_script.
"""
from . import setup_hopla_application

if __name__ == "__main__":
    setup_hopla_application()
