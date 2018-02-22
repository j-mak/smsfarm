PYTHON=/usr/bin/env python3

install:
	$(PYTHON) setup.py develop

freeze:
	pip freeze | grep -v "pkg-resources" > requirements.txt

tests-all: tests pep8 pylint

test:
	$(PYTHON) -m unittest tests/test_*

test-verbose:
	$(PYTHON) -m unittest -v tests/test_*

pep8:
	$(PYTHON) -m pycodestyle --show-pep8 --max-line-length=80 smsfarm

pylint:
	$(PYTHON) -m pylint --output-format=colorized smsfarm

pylint-reports:
	$(PYTHON) -m pylint --reports=yes smsfarm
