.PHONY: docs clean
TEST ?= 

docs: clean
	sphinx-apidoc -o docs src/
	cd docs && make html

clean:
	rm -rf docs/_build

autoformat:
	black src

lint:
	pylint --output-format=parseable,colorized --disable=C0301 src

coverage:
	coverage run -m pytest $(TEST)
	coverage html
	open htmlcov/index.html

check: 
	$(MAKE) autoformat
	$(MAKE) lint