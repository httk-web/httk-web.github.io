#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

from httk.web import publish

ROOT = Path(__file__).parent

# URL style for generated links in publish mode:
# - False => links include ".html" suffix (for broad static-host compatibility)
# - True  => extensionless links
USE_URLS_WITHOUT_EXT = False

docs = ROOT / "docs"
docs.mkdir(parents=True, exist_ok=True)

# Clean docs/ but preserve dotfiles (e.g. docs/.gitignore, docs/.nojekyll).
for entry in os.listdir(docs):
    if entry.startswith("."):
        continue
    target = docs / entry
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()

# Main site: src/ -> docs/
publish(ROOT / "src", docs, "http://127.0.0.1/", use_urls_without_ext=USE_URLS_WITHOUT_EXT)

# Legacy httk v1 subsite: src-v1/ -> docs/v1/
(docs / "v1").mkdir(parents=True, exist_ok=True)
publish(ROOT / "src-v1", docs / "v1", "http://127.0.0.1/v1/", use_urls_without_ext=USE_URLS_WITHOUT_EXT)

print("*****\nNow open docs/index.html in your web browser.\n*****")
