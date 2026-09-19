---
title: "Quickstart: websites and UI"
template: default
base_template: base_default
---

# *httk* quickstart: websites and UI

*httk-serve* provides dynamic serving and static publishing of websites under
`httk.serve.web`, and generic OPTIMADE protocol serving under
`httk.serve.optimade`. This very website is generated with it.

## Create a simple static website

A site is a source directory with content pages and Jinja2 templates:
```
mysite/
  src/
    content/
      index.md
    templates/
      base_default.html.j2
      default.html.j2

```
Content pages are Markdown or reStructuredText with a small front-matter
header:

```markdown
---
title: My first httk-serve page
template: default
---

# Hello from httk-serve

Pages are Markdown or reStructuredText rendered through Jinja2 templates.

```
Serve it live during development, with pages re-rendered per request:

```python
from pathlib import Path

from httk.serve.web import serve

ROOT = Path(__file__).parent
serve(ROOT / "src", port=8080)

```
And publish the same source tree as a static website, ready for any static
host such as GitHub Pages:

```python
from pathlib import Path

from httk.serve.web import publish

ROOT = Path(__file__).parent
publish(ROOT / "src", ROOT / "public", "https://example.org/")

```
Complete runnable site examples — including a blog and a search application —
are in the `examples/modern/` directory of the [httk-serve repository](https://github.com/httk/httk-serve). The source of this website itself is
another real-world example, at [https://github.com/httk/httk-web.github.io](https://github.com/httk/httk-web.github.io).

## Serve data over OPTIMADE

Start with a few CIF files and a JSON table of energies. This example serves
both `structures` and `_httk_records`, with each energy record linked to its
structure. First import the files into SQLite, then serve that database.

With Python 3.12 or newer, install:

```bash
python -m pip install 'httk-atomistic[default]' 'httk-store[db]' httk-serve
```

Put your CIF files in a `cifs/` directory. To try the example as written,
download [NaCl.cif](examples/optimade/NaCl.cif) and
[MgO.cif](examples/optimade/MgO.cif) into it. Beside that directory, save
`results.json`:

```json
[
  {"cif": "NaCl.cif", "formation_energy": -1.2},
  {"cif": "MgO.cif", "formation_energy": -0.8}
]
```

These are invented demonstration energies in eV per atom, associated with the
CIF named by each row.

The three small scripts below separate the record definition, database build,
and server. The `EntryRecord` helpers supply the storage and OPTIMADE plumbing;
the class only says what a result contains. These helpers are currently
unreleased, so use matching development checkouts of `httk-core` and
`httk-store` when trying this example.

Save this as `result_record.py` beside `results.json`:

```python
from typing import Annotated

from httk.atomistic import UnitcellStructureRecord
from httk.core import DataEntryRecord, Property, entry_record


@entry_record("example.result")
class Result(DataEntryRecord):
    formation_energy: Annotated[
        float,
        Property(
            unit="eV",
            description="Formation energy per atom relative to elemental reference phases.",
        ),
    ]
    structure: UnitcellStructureRecord
```

The energy is published as `_httk_custom_formation_energy`; the ordinary
`structure` field becomes a relationship to `structures`.

Save this as `build_db.py`:

```python
import json
from pathlib import Path

from httk.atomistic import UnitcellStructureRecord, UnitcellStructureView
from httk.core import load
from httk.store import EntryIdScheme, SqliteStore
from result_record import Result


store = SqliteStore(
    "results.sqlite", records=[Result], entry_ids=EntryIdScheme("example", "1")
)
for row in json.loads(Path("results.json").read_text()):
    sid = store.save(UnitcellStructureView(load(Path("cifs") / row["cif"])))
    structure = store.fetch(UnitcellStructureRecord, sid)
    store.save(Result(row["formation_energy"], structure))
store.close()
```

Save this as `serve_db.py`:

```python
from httk.serve.optimade import serve
from httk.store import SqliteStore
from result_record import Result


store = SqliteStore("results.sqlite", records=[Result])
serve(store, port=8080)
store.close()
```

Run the import once, then start the API:

```bash
python build_db.py
python serve_db.py
```

The server reads the persisted database directly; it does not need the JSON or
CIF files. Repeating the build deduplicates unchanged data.

In another terminal, list the structures or select energies below −1 eV/atom
together with their linked structures:

```bash
curl http://127.0.0.1:8080/v1/structures
curl --get http://127.0.0.1:8080/v1/_httk_records \
  --data-urlencode 'filter=_httk_custom_formation_energy < -1' \
  --data-urlencode 'include=structures'
```

The filtered response contains the NaCl result with
`attributes._httk_custom_formation_energy` equal to `-1.2`. Its
`relationships.structures` points to the saved structure, and `included`
contains that structure's lattice, sites, and species. Visit
`/v1/info/_httk_records` to see the energy property's definition.

For more on database queries and serving, see the
[SQLite serving walkthrough](https://docs.httk.org/dev/main/serving-data.html).
The API runs as a Python service; GitHub Pages can host a companion website.

## More

See the [serve documentation](https://docs.httk.org/httk-serve/dev/main/) for
widgets, trusted assets, the ASGI runtime, and the OPTIMADE serving and client
layers.
