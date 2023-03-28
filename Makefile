black:
	black --preview src tests

pylint:
	pylint --disable=R,C src tests

mypy:
	mypy src tests

test:
	python3 -m unittest discover -s tests

coverage:
	coverage run --source=src -m unittest discover -s tests
	coverage report

lint: black pylint mypy

all: lint coverage

