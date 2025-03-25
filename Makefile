.PHONY: docs clean

docs: clean
	sphinx-apidoc -o docs src/
	cd docs && make html

clean:
	rm -rf docs/_build

autoformat:
	black src

lint:
	pylint --output-format=parseable,colorized src

check: 
	black src
	pylint --output-format=parseable,colorized src