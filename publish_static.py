#!/usr/bin/env python3

import shutil
from pathlib import Path

from httk.web import publish

ROOT = Path(__file__).parent

# Publish target base URL (used for page.absurl style fields).
BASEURL = "https://httk.org/"

# URL style for generated links in publish mode:
# - False => links include ".html" suffix (for broad static-host compatibility)
# - True  => extensionless links
USE_URLS_WITHOUT_EXT = False

public = ROOT / "public"
if public.exists():
    shutil.rmtree(public)

# Main site: src/ -> public/
publish(ROOT / "src", public, BASEURL, use_urls_without_ext=USE_URLS_WITHOUT_EXT)

# Legacy httk v1 subsite: src-v1/ -> public/v1/
(public / "v1").mkdir(parents=True, exist_ok=True)
publish(ROOT / "src-v1", public / "v1", BASEURL + "v1/", use_urls_without_ext=USE_URLS_WITHOUT_EXT)

print("*****\nNow open public/index.html in your web browser.\n*****")
