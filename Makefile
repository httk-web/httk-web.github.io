PYTHON ?= python3

.PHONY: generate serve serve_static clean

generate:
	$(PYTHON) ./publish_static.py

serve:
	$(PYTHON) ./serve_dynamic.py

serve_static: generate
	echo "Open: http://localhost:8080/index.html"
	cd public && $(PYTHON) -m http.server 8080

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	find . -name "*~" -print0 | xargs -0 rm -f
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
