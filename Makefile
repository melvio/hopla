build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

develop:
	pip install --upgrade --editable .


# This works like running: "make lint && make unittest && make doctest"
test: lint unittest


lint:
	pylint $$(find src/ -name "*.py") --rcfile=./.github/workflows/pylintrc.conf

unittest:
	pytest
