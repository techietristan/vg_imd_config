install:
	python -m pip install  pipenv
	pipenv sync

dev:
	pipenv check
	pipenv sync --dev
	pymon tests/run_all_unit_tests.py -p *.py

test:
	coverage xml
	coverage run -m unittest discover