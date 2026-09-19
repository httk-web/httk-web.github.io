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
  {"sample": "nacl-demo", "cif": "NaCl.cif", "formation_energy": -1.2},
  {"sample": "mgo-demo", "cif": "MgO.cif", "formation_energy": -0.8}
]
```

These are invented demonstration energies in eV per atom. Use a unique
`sample` label for each result; several results can refer to the same CIF.

Save this as `import_data.py` beside `results.json`. `Result` defines an
energy record and a `StrongLink` to its structure. The remaining class metadata
tells OPTIMADE how to describe and filter the energy field.

```python
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, ClassVar

from httk.atomistic import StructureEntry, UnitcellStructureRecord, UnitcellStructureView
from httk.core import PropertyDefinition, RunEdge, load, load_entry_type_definition
from httk.core.data_records import RECORDS_DEFINITION_ID
from httk.core.register import register_entry_family, register_entry_record
from httk.core.storage import IdentitySkip, Indexed, StorageInfo, StoredPropertyProjection, StrongLink, Unique
from httk.store import EntryIdScheme, SqliteStore

energy = PropertyDefinition.from_simple(
    "_httk_custom_formation_energy",
    description="Formation energy per atom relative to elemental reference phases.",
    fulltype="float", unit="eV",
)

@dataclass(frozen=True)
class Result:
    """An energy result with a stored link to its structure."""

    sample: str
    formation_energy: float
    structure: Annotated[tuple[RunEdge, ...], StrongLink("structure", role="subject")]
    id: Annotated[str | None, IdentitySkip(), Indexed()] = field(default=None, compare=False)
    immutable_id: Annotated[str | None, IdentitySkip(), Unique()] = field(default=None, compare=False)

    type: ClassVar = "records"
    definition_id: ClassVar = RECORDS_DEFINITION_ID
    __httk_storage__: ClassVar = StorageInfo(storage_name="example_result", identity_name="example.result")
    __httk_stored_properties__: ClassVar = {
        energy.name: StoredPropertyProjection(
            response=lambda record: record.formation_energy,
            query=lambda context, operator, value: context.compare(
                context.field("formation_energy"), operator, context.constant(value)
            ),
        ),
    }

    @classmethod
    def entry_type_definition(cls):
        """Describe the energy served on the records endpoint."""
        return load_entry_type_definition(cls.definition_id).extended({energy.name: energy})

register_entry_family(name="example-results", family=f"{__name__}:Result", definition_id=RECORDS_DEFINITION_ID)
register_entry_record(name="example-result", record=f"{__name__}:Result", family="example-results")

root = Path(__file__).parent

def open_store():
    """Open the results database with its structure and energy record layouts."""
    return SqliteStore(
        root / "results.sqlite",
        entry_records={StructureEntry: UnitcellStructureRecord, Result: Result},
        entry_ids=EntryIdScheme("example", "1"),
    )

if __name__ == "__main__":
    rows = json.loads((root / "results.json").read_text())
    with open_store() as store, store.transaction():
        for row in rows:
            sid = store.save(UnitcellStructureView(load(root / "cifs" / row["cif"])))
            structure = store.fetch(UnitcellStructureRecord, sid)
            store.save(Result(
                row["sample"], row["formation_energy"],
                (RunEdge("structure", "structures", structure.id),),
            ))
```

`store.save()` stores each structure and result. The link is part of the result's
content; `RunEdge` holds the stored structure's public ID. The transaction keeps
the import together, and repeating an unchanged import deduplicates the data.
The custom energy attribute is published as `_httk_custom_formation_energy`.

Now save the serving script as `api.py` in the same directory:

```python
from import_data import open_store
from httk.serve.optimade import serve

with open_store() as store:
    serve(store, port=8080)
```

Run the import once, then start the API:

```bash
python import_data.py
python api.py
```

Importing `open_store` loads the record definition without running the import
loop. The server reads the persisted database directly; it does not need the
JSON or CIF files. The `with` block closes the store when the server stops.

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
`relationships._httk_structure` points to the saved structure, and `included`
contains that structure's lattice, sites, and species. The store assigns the
public IDs. Visit `/v1/info/_httk_records` to see the energy property's definition.

For more on database queries and serving, see the
[SQLite serving walkthrough](https://docs.httk.org/dev/main/serving-data.html).
The API runs as a Python service; GitHub Pages can host a companion website.

## More

See the [serve documentation](https://docs.httk.org/httk-serve/dev/main/) for
widgets, trusted assets, the ASGI runtime, and the OPTIMADE serving and client
layers.
