PYTHON ?= python3
PY_SOURCES := serve_dynamic.py publish_static.py

.PHONY: serve generate serve_static clean format format-check lint typecheck test

serve:
	python3 ./serve_dynamic.py

generate:
	python3 ./publish_static.py

serve_static: generate
	echo "Open:"
	echo "* http://localhost:8080/index.html"
	cd docs && python3 -m http.server 8080

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	find . -name "*~" -print0 | xargs -0 rm -f
	find . -name "__pycache__" -print0 | xargs -0 rm -rf

format:
	$(PYTHON) -m ruff check $(PY_SOURCES) --select F401 --fix
	$(PYTHON) -m isort $(PY_SOURCES)
	$(PYTHON) -m black $(PY_SOURCES)

format-check:
	$(PYTHON) -m isort --check-only $(PY_SOURCES)
	$(PYTHON) -m black --check $(PY_SOURCES)

lint:
	$(PYTHON) -m ruff check $(PY_SOURCES)

typecheck:
	$(PYTHON) -m mypy
