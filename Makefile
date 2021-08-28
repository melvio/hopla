


build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

develop:
	pip install --upgrade -e .

lint:
	pylint $$(find src/ -name "*.py") --rcfile=./.github/workflows/pylintrc.conf

