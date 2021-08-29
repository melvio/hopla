build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

develop:
	pip install --upgrade --editable .

lint:
	pylint $$(find src/ -name "*.py") --rcfile=./.github/workflows/pylintrc.conf


doctest:
	python -m doctest --verbose src/hopla/cli/groupcmds/get.py


# TODO: create a coveragerc and add it to the github workflow
coverage_failure_threshold=40
unittest:
	pytest --cov='hopla.hoplalib' --cov='hopla.cli' \
		--cov-branch \
		--cov-fail-under=$(coverage_failure_threshold) \
		src/hopla/tests/
