.PHONY: docs clean
TEST ?= ""

html-docs: clean
	sphinx-apidoc -o docs src/apache_commons_validator_python/
	cd docs && make html

check-latex:
	@command -v pdflatex >/dev/null 2>&1 && echo "✅ pdflatex is installed." || { \
		echo "❌ pdflatex not found in PATH."; \
		echo ""; \
		OS=$$(uname); \
		if [ "$$OS" = "Darwin" ]; then \
			echo "🔧 macOS: Run 'brew install --cask mactex'"; \
		elif [ "$$OS" = "Linux" ]; then \
			echo "🔧 Linux: Run 'sudo apt install texlive-full'"; \
		elif [ "$$OS" = "MINGW64_NT" ] || [ "$$OS" = "MSYS_NT" ] || [ "$$OS" = "CYGWIN_NT" ]; then \
			echo "🔧 Windows: Install MiKTeX from https://miktex.org/download and add it to PATH."; \
		else \
			echo "🔧 Unknown OS: Please install a LaTeX distribution manually."; \
		fi; \
		exit 1; }

pdf-docs: check-latex clean 
	sphinx-apidoc -o docs src/apache_commons_validator_python/
	cd docs && make pdf

clean:
	find . -type f -name '*.rst' ! -name 'index.rst' -delete
	rm -rf docs/_build
	rm -rf .coverage htmlcov
	
autoformat:
	black src

lint:
	pylint --output-format=parseable,colorized --disable=C0301 src

coverage:
	-coverage run --branch -m pytest $(TEST)
	-mkdir htmlcov
	-echo "" > htmlcov/coverage_report.txt
	-coverage report -m > htmlcov/coverage_report.txt
	-coverage html
	-open htmlcov/index.html
	
check: 
	$(MAKE) autoformat
	$(MAKE) lint
	$(MAKE) coverage

mutation:
	PYTHONPATH=. mutmut run
