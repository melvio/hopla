"""
Module that sets __version__ and then calls the kickstarter.
"""

from hopla.hoplalib.hoplaversion import HoplaVersion

__version__ = HoplaVersion().semantic_version()
""" This __version__ is read by setup.cfg. """

try:
    from hopla.kickstart import hopla, kickstart_hopla


    def setup_hopla_application():
        """
        This function only calls kickstart_hopla. This reduces the
        required logic in base __init__.py
        """
        kickstart_hopla()

except ModuleNotFoundError as ex:
    pass
    # This error catching is just here for the `python -m build` call that
    # fails to find click at build time when trying to find the
    # __version__ variable.
