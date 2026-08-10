---
title: "Quickstart: databases"
template: default
base_template: base_default
---

# *httk* quickstart: databases

*httk-store* provides relational storage and querying over SQLite and DuckDB,
built on plain frozen dataclasses — no base classes, no ORM sessions. Exact
values (rationals, surd cell bases) are stored exactly. The examples below need
*httk-store* and *httk-atomistic* installed.

## Create a database file, store a structure in it, and retrieve it

The first opening of a store declares which durable record layouts it may
contain; here every stored structure uses the normalized
`UnitcellStructureRecord` layout:

```python
from httk.atomistic import (
    StructureEntry,
    UnitcellStructure,
    UnitcellStructureRecord,
    UnitcellStructureView,
)
from httk.store.db import Database, SqlStore

structure = UnitcellStructure(
    cell=[["5.64", 0, 0], [0, "5.64", 0], [0, 0, "5.64"]],
    sites=[
        [0, 0, 0], ["1/2", "1/2", 0], ["1/2", 0, "1/2"], [0, "1/2", "1/2"],
        ["1/2", "1/2", "1/2"], [0, 0, "1/2"], [0, "1/2", 0], ["1/2", 0, 0],
    ],
    species_at_sites=["Na", "Na", "Na", "Na", "Cl", "Cl", "Cl", "Cl"],
)

store = SqlStore(
    Database.sqlite("example.sqlite"),
    entry_records={StructureEntry: UnitcellStructureRecord},
)

sid = store.save(structure)
fetched = store.fetch(UnitcellStructureRecord, sid)
restored = UnitcellStructureView(fetched)
print("Saved row", sid, "with stable structure id", restored.id)

```
`save()` accepts the natural structure object and projects its cell, sites,
species, and composition recursively — there is no manual record-conversion
step. The hexadecimal `.id` is a content hash: structural, and stable across
equivalent objects and stores. The integer `sid` is only a local relational
row identifier. Saving an equal structure again deduplicates to the same row.

`Database.sqlite()` without a filename creates an in-memory database;
`Database.duckdb(...)` works the same way.

## Search the database

Bind a variable to a record class, add conditions, and freeze the query with
`results()`:

```python
search = store.searcher()
s = search.variable(UnitcellStructureRecord)
search.add(s.species_at_sites.has_any("Cl"))

for row in search.results(structure=s):
    print("Found:", UnitcellStructureView(row.structure).formula)

```
Running this generates the output:
```
Found: ClNa

```
List fields have set operations (`has_any`, `has_only`, `is_in`),
references chain into automatic joins, and two variables of the same class form
a self-join.

## Store your own data

Any frozen dataclass whose field types resolve is storable. Storage behavior is
tuned with `typing.Annotated` markers from *httk-core* (`Indexed`,
`Unique`, `Skip`, `Shape`, ...), and rational values round-trip exactly:

```python
from dataclasses import dataclass
from fractions import Fraction
from typing import Annotated

from httk.core import Indexed
from httk.store.db import Database, SqlStore

@dataclass(frozen=True)
class Measurement:
    formula: Annotated[str, Indexed()]
    spacegroup: int
    energy: Fraction

store = SqlStore(Database.sqlite(), entry_records={})
sid = store.save(Measurement("NaCl", 225, Fraction(-13, 3)))
store.save(Measurement("MgO", 225, Fraction(-29, 7)))

print("Energy round-trips exactly:", store.fetch(Measurement, sid).energy)

search = store.searcher()
m = search.variable(Measurement)
search.add(m.spacegroup == 225)
for row in search.results(measurement=m):
    print(row.measurement.formula, row.measurement.energy)

```
Running this generates the output:
```
Energy round-trips exactly: -13/3
NaCl -13/3
MgO -29/7

```
The explicit `entry_records={}` declares a store containing only private
custom dataclasses.

## More

The top-site [data guide](https://docs.httk.org/dev/main/data/) gives the
ecosystem overview. The full [database details](https://docs.httk.org/httk-store/dev/main/details/db/) cover child tables
and references, content-based deduplication, cursors, store federation, and
serving a store over the OPTIMADE protocol.
