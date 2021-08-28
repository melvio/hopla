build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

develop:
	pip install --upgrade --editable .

lint:
	pylint $$(find src/ -name "*.py") --rcfile=./.github/workflows/pylintrc.conf


doctest:
	python -m doctest --verbose src/hopla/cli/groupcmds/get.py

unittest:
	pytest src/hopla/tests/