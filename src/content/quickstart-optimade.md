---
title: "Quickstart: OPTIMADE client"
template: default
base_template: base_default
---

# *httk* quickstart: OPTIMADE client

[OPTIMADE](https://www.optimade.org/) is a common REST API for materials
databases, so the same query language and response format work across dozens
of independent databases. *httk-store* (part of the `httk2` metapackage)
provides `OptimadeStore`, a read-only client that discovers a service and
exposes it through the same query interfaces as a local *httk* database. The
examples below need network access; they were run against public providers and
the outputs shown are from the time of writing. Use
[providers.optimade.org](https://providers.optimade.org/) to find other
endpoints, then assign your chosen base URL to `base_url`.

## Connect and discover

Point `OptimadeStore` at a service base URL. Version negotiation and schema
discovery happen up front, so the API version and the available entry types
are known immediately:

```python
from httk.store.optimade import OptimadeStore

base_url = "https://alexandria.icams.rub.de/pbe"

store = OptimadeStore(base_url)
print("API version:", store.api_version)
for entry_type in store.entry_types:
    print("Entry type:", entry_type.name)

```
Running this generates the output:
```
API version: 1.1.0
Entry type: structures
Entry type: references

```
## Filter remote entries

Queries use the *httk-store* searcher: bind a variable to an entry type, add
conditions, and freeze the query with `results()`. The conditions are
translated into the OPTIMADE filter language
(`chemical_formula_reduced = "ClNa" AND nsites = 2`), and `search.count()`
asks the service how many entries match, for services that report counts.
Standard OPTIMADE
properties and provider-specific ones (here prefixed `_alexandria_`) are
available as attributes of the variable:

```python
search = store.searcher()
s = search.variable(store.entry_type("structures"))
search.add((s.chemical_formula_reduced == "ClNa") & (s.nsites == 2))
for row in search.results(structure=s, nsites=s.nsites, spacegroup=s._alexandria_space_group):
    print(row.structure.id, row.nsites, row.spacegroup)

```
Running this generates the output:
```
agm003157609 2 225
agm005244656 2 221

```
Results are fetched page by page as you iterate, so a query over a large
database only transfers the rows you consume.

## Pandas-style slicing

`store.slicer(...)` wraps the same query machinery in a `[]` indexing surface;
here it repeats the selection above in pandas style.
A field name gives a column, comparisons give boolean masks that combine with
`&`, `|`, and `~`, and indexing with a mask selects the matching entries:

```python
structures = store.slicer("structures")
selected = structures[(structures["chemical_formula_reduced"] == "ClNa") & (structures["nsites"] == 2)]
for entry in selected:
    print(entry.id, entry._alexandria_space_group, entry._alexandria_band_gap)

store.close()

```
Running this generates the output:
```
agm003157609 225 5.0101
agm005244656 221 3.9791

```
## Load a remote structure into *httk*

A remote structure entry is turned into an ordinary *httk* structure by
constructing a view, exactly as for local data. From there everything in the
[structures quickstart](quickstart-structures.html) applies, e.g., saving the
structure as a CIF file:

```python
from httk.atomistic import UnitcellStructureView
from httk.core import save
from httk.store.optimade import OptimadeStore

with OptimadeStore("https://altermagnets.anyterial.se/optimade/amdb") as store:
    search = store.searcher()
    s = search.variable(store.entry_type("structures"))
    search.add(s.chemical_formula_reduced == "CrSb")
    remote = search.results(structure=s).first().structure

structure = UnitcellStructureView(remote)
print("Formula:", structure.formula)
print("Number of sites:", len(structure.sites))
print("Volume:", round(float(structure.cell.volume), 3))
save(structure, "CrSb.cif")

```
Running this generates the output:
```
Formula: CrSb
Number of sites: 4
Volume: 79.646

```
The conversion is lazy and keeps the exact remote resource: `remote` retains
the complete OPTIMADE record, while the view decodes cell, sites, and species
only when they are accessed.

*httk* identifies properties by their OPTIMADE property definitions rather
than by name, so loading a remote entry as a structure requires a service that
publishes property definitions (OPTIMADE v1.2 or later, such as the example
above, which is served by *httk-serve*). Older services, such as the v1.1
provider used in the first examples, can still be discovered, filtered, and
read attribute by attribute as shown above.

## More

Relationship queries (`s.links.<name>`), following provenance between entry
types, sorting, and the client's pagination and error-handling contracts are
covered in the [httk-store documentation](https://docs.httk.org/httk-store/).
Serving your own data over OPTIMADE is described in the
[websites and UI quickstart](quickstart-httk-serve.html).
