from setuptools import setup

MAJOR_VERSION = 0
MINOR_VERSION = 0
PATCH_VERSION = 1
PRE_RELEASE = "alpha"


def hopla_version() -> str:
    # <https://semver.org/>
    # TODO: get this value injected into `hopla version`

    version_core = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
    if PRE_RELEASE is not None and PRE_RELEASE is not "":
        pre_release = f"-{PRE_RELEASE}"
    else:
        pre_release = ""

    return version_core + pre_release


setup(
    name="hopla",
    version=hopla_version(),
    author="Melvin",
    url="https://github.com/melvio/hopla",
    py_modules=["main"],
    # https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=[
        "Click",
        "requests"
    ],
    entry_points={
        'console_scripts': {
            'main = main:hopla'
        }
    }
)
