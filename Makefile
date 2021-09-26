build:
	# https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html
	python -m build && pip install .

clean:
	rm -r dist/*

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


# This works like running: "make lint && make unittest"
test: lint unittest


lint:
	pylint $$(find src/ -name "*.py") --rcfile=./.github/workflows/pylintrc.conf

unittest:
	pytest -c ./.github/workflows/pytest.ini
