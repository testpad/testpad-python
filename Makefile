
install:
	pip install -U pip wheel poetry
	poetry install
	pre-commit install

test:
	pytest
