"""
Module that sets __version__ and then calls the kickstarter.
"""

from hopla.hoplalib.hoplaversion import HoplaVersion

try:
    # F401=module-imported-but-unused: hopla.kickstart.hopla is indeed
    # imported but not use directly. However, we still need it for
    # need it for build the right now.
    from hopla.kickstart import hopla  # noqa: F401
    from hopla.kickstart import kickstart_hopla

except ModuleNotFoundError:
    pass
    # This error catching is just here for the `python -m build` call that
    # fails to find click at build time when trying to find the
    # __version__ variable.

__version__ = HoplaVersion().semantic_version()
""" This __version__ is read by setup.cfg. """


def setup_hopla_application():
    """
    This function only calls kickstart_hopla. This reduces the
    required logic in base __init__.py
    """
    kickstart_hopla()
