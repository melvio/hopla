from setuptools import setup

# TODO: get this value injected into `hopla version`
HOPLA_VERSION = "0.0.1"

setup(
    name="hopla",
    version=HOPLA_VERSION,
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
