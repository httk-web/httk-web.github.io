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
structure. It loads the files into memory when the server starts.

With Python 3.12 or newer, install:

```bash
python -m pip install 'httk-atomistic[default]' httk-store httk-serve
```

Put your CIF files in a `cifs/` directory. To try the example as written,
download [NaCl.cif](examples/optimade/NaCl.cif) and
[MgO.cif](examples/optimade/MgO.cif) into it. Beside that directory, save
`results.json`:

```json
[
  {"sample": "nacl-demo", "cif": "NaCl.cif", "formation_energy": -1.2},
  {"sample": "mgo-demo", "cif": "MgO.cif", "formation_energy": -0.8}
]
```

These are invented demonstration energies in eV per atom. Use a unique
`sample` label for each result; several results can refer to the same CIF.

Save this as `api.py` beside `results.json`:

```python
import json
from pathlib import Path

from httk.atomistic import StructureEntryProvider, UnitcellStructureView
from httk.core import DataRecord, PropertyDefinition, RelatedEntry, load
from httk.serve.optimade import adapter_from_providers, serve
from httk.store import DataRecordEntryProvider

energy = PropertyDefinition.from_simple(
    "_httk_custom_formation_energy",
    description="Formation energy per atom relative to elemental reference phases.",
    fulltype="float",
    unit="eV",
)

root = Path(__file__).parent
rows = json.loads((root / "results.json").read_text())
structures, records, links = {}, {}, {}
for row in rows:
    sample, cif = row["sample"], row["cif"]
    structures[cif] = UnitcellStructureView(load(root / "cifs" / cif))
    records[sample] = DataRecord.from_value(
        energy.definition_id, energy.name, row["formation_energy"]
    )
    links[sample] = [RelatedEntry("structures", cif, label="structure", role="subject")]

adapter = adapter_from_providers([
    StructureEntryProvider(structures),
    DataRecordEntryProvider(
        records, definitions={energy.name: energy}, relationships=links
    ),
])

if __name__ == "__main__":
    serve(adapter, port=8080)
```

The two providers handle the OPTIMADE representation of structures and results.
`RelatedEntry` connects each result to its structure. The energy definition
supplies its meaning, type, and unit; `_httk_custom_` is the prefix for this
example's custom API attribute.

Start the server with `python api.py`. In another terminal, list the structures
or select energies below −1 eV/atom together with their linked structures:

```bash
curl http://127.0.0.1:8080/v1/structures
curl --get http://127.0.0.1:8080/v1/_httk_records \
  --data-urlencode 'filter=_httk_custom_formation_energy < -1' \
  --data-urlencode 'include=structures'
```

The filtered response contains the `nacl-demo` result with
`attributes._httk_custom_formation_energy` equal to `-1.2`. Its
`relationships.structures` points to `NaCl.cif`, and `included` contains that
structure's lattice, sites, and species. Visit `/v1/info/_httk_records` to see
the energy property's definition.

This is a small-dataset example: restart the server after changing the input
files. For a persistent database, custom result classes, and Python queries
such as `record.formation_energy` and `record.links.structure`, continue with
the [SQLite serving walkthrough](https://docs.httk.org/dev/main/serving-data.html).
The API runs as a Python service; GitHub Pages can host a companion website.

## More

See the [serve documentation](https://docs.httk.org/httk-serve/dev/main/) for
widgets, trusted assets, the ASGI runtime, and the OPTIMADE serving and client
layers.
