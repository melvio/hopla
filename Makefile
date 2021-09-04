build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

develop:
	pip install --upgrade --editable .


# This works like running: "make lint && make unittest && make doctest"
test: lint unittest doctest


lint:
	pylint $$(find src/ -name "*.py") --rcfile=./.github/workflows/pylintrc.conf


doctest:
	python -m doctest --verbose src/hopla/cli/groupcmds/get.py \
                                src/hopla/cli/groupcmds/add.py

# TODO: create a coveragerc and add it to the github workflow
coverage_failure_threshold=40
unittest:
	pytest
