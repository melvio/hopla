build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

clean:
	rm -r -- dist/*

clean_build: clean build

develop:
	pip install --upgrade --editable .

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#uploading-your-project-to-pypi
# Tip: The reStructuredText parser used on PyPI is not Sphinx! Furthermore, to
# ensure safety of all users, certain kinds of URLs and directives are
# forbidden or stripped out (e.g., the .. raw:: directive). Before trying to
# upload your distribution, you should check to see if your
# brief / long descriptions provided in setup.py are valid. You can do this
# by running twine check on your package files:
validate_docs_for_pypi:
	twine check dist/*


send_package_to_pypi:
	python -m twine upload dist/*

tag_commit:
	git tag --annotate "release/$$(hopla version)"


tag_push:
	git push --tags



# This works like running: "make flake && make lint && make unittest"
test: flake lint unittest


flake:
	flake8 --config="./.github/workflows/flake8.ini" src/ setup.py


lint:
	pylint $$(find src/ -name "*.py") setup.py --rcfile=./.github/workflows/pylintrc.conf

unittest:
	pytest -c ./.github/workflows/pytest.ini


release: test clean_build develop validate_docs_for_pypi send_package_to_pypi tag_commit tag_push
