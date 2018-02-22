PYTHON=/usr/bin/env python3

install:
	$(PYTHON) setup.py develop

freeze:
	pip freeze | grep -v "pkg-resources" > requirements.txt

tests: unittests pep8 pylint

unittests:
	$(PYTHON) -m unittest tests/test_*

unittests_verbose:
	$(PYTHON) -m unittest -v tests/test_*

pep8:
	$(PYTHON) -m pycodestyle --show-pep8 --max-line-length=80 smsfarm

pylint:
	$(PYTHON) -m pylint --output-format=colorized smsfarm

pylint-reports:
	$(PYTHON) -m pylint --reports=yes smsfarm