#!/usr/bin/env python3
import logging
import os
import sys

sys.path.append(os.environ.get("script_dirname"))

log = logging.getLogger()

# TODO: temporary, while hopla is in beta
try:
    # jetbrains
    from hopla.hoplalib.Authorization import AuthorizationHandler
except:
    # cmdline
    from ..hoplalib.Authorization import AuthorizationHandler

if __name__ == "__main__":
    AuthorizationHandler().set_hopla_credentials(overwrite=True)
