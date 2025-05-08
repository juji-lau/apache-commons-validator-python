.PHONY: docs clean
TEST ?= 

docs: clean
	sphinx-apidoc -o docs src/
	cd docs && make html

clean:
	rm -rf docs/_build
	rm -rf .coverage htmlcov
	
autoformat:
	black src

lint:
	pylint --output-format=parseable,colorized --disable=C0301 src

coverage:
	coverage run --branch -m pytest $(filter-out $@,$(MAKECMDGOALS)) || true
	coverage report -m >> htmlcov/coverage_report.txt
	coverage html
	open htmlcov/index.html

check: 
	$(MAKE) autoformat
	$(MAKE) lint
	$(MAKE) coverage