.PHONY: docs clean

docs: clean
	sphinx-apidoc -o docs src/
	cd docs && make html

clean:
	rm -rf docs/_build