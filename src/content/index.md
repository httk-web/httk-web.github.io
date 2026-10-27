---
title: Front page
template: front
base_template: base_default
---

# The High-Throughput Toolkit (*httk₂*)

The High-Throughput Toolkit (*httk₂*) is an open-source toolkit for *preparing* and *running* automated computational workflows, *analyzing* the results, *store* them in a global and/or in a personalized database, and providing *UI and API access to tha data.* Presently, *httk₂* is primarily targeted at atomistic calculations in materials science and electronic structure, but aims to be more broadly useful outside those areas.

The first version of *httk* was released in 2014. This site documents *httk₂*, maintained mainly by the [Unit of Materials Design and Informatics](https://liu.se/en/research/materials-design-and-informatics) at [Theoretical Physics](https://liu.se/en/research/theoretical-physics) at [Linköping University](https://www.liu.se/) (LiU) in Sweden. The lead developer and maintainer is [Rickard Armiento](https://liu.se/en/employee/ricar47). The AUTHOR files in the respective source code repositories list significant contributors.

**For an inventory of other software project and datasets we are involved in, see the [Anyterial](https://www.anyterial.se) website.**

<div class="alert alert-secondary" role="alert">
<strong>Looking for <i>httk</i> v1?</strong> The legacy website is available at
<a href="https://httk.org/v1">httk.org/v1</a>, documentation at
<a href="https://olddocs.httk.org">olddocs.httk.org</a>, and source code at
<a href="https://github.com/httk/httk">github.com/httk/httk</a>.
<strong>Note that <i>httk</i> v1 and <i>httk₂</i> cannot be installed in the same Python environment.</strong>
</div>

*httk₂* is a rewrite of *httk v1* as a **modular toolkit**: its functionality is split across a set of independent module repositories that share a common, PEP 420 native `httk.*` namespace (`httk.core`, `httk.atomistic`, `httk.store`, and more) where `httk.core` provides a shared plugin, loading, and view/backend machinery the other modules build on. This layout allows dependencies to be resolved with just the parts needed.

<div class="alert alert-warning" role="alert">
<strong>⚠ BETA</strong> The organization of <i>httk₂</i> packages and their APIs is not yet stable, and there may be backward-breaking changes between v2.1.* versions.
</div>

<h2 id="installation">Installation</h2>

*httk₂* requires Python 3.12 or newer. The `httk2` metapackage installs the complete standard set of *httk₂* modules, each with its recommended default features, in one step:

**Short version**

```bash
pip install httk2
```
If you are a frequent user of, e.g., the VASP simulation software you can get our support packages included via a so called PIP extra, e.g.:
```bash
pip install httk2[vasp]
```
Other valid options are: `qe` (Quantum Esspresso), `abinit`, `cp2k`, `gromacs`, `lammps`, `orca`.

Individual modules can also be installed on their own, e.g., `pip install httk-atomistic`; see the [httk2 README](https://github.com/httk/httk2#readme) for the list of modules.

**Different tools and dev use**

We recommend installing into a virtual environment. Pick your preferred tool:

<ul class="nav nav-tabs" role="tablist">
<li class="nav-item"><a class="nav-link active" data-toggle="tab" href="#install-venv" role="tab">venv</a></li>
<li class="nav-item"><a class="nav-link" data-toggle="tab" href="#install-uv" role="tab">uv</a></li>
<li class="nav-item"><a class="nav-link" data-toggle="tab" href="#install-conda" role="tab">conda</a></li>
<li class="nav-item"><a class="nav-link" data-toggle="tab" href="#install-git-venv" role="tab">git + venv</a></li>
<li class="nav-item"><a class="nav-link" data-toggle="tab" href="#install-git-conda" role="tab">git + conda</a></li>
</ul>
<div class="tab-content">
<div class="tab-pane fade show active" id="install-venv" role="tabpanel">

```bash
python3 --version           # check that you have Python 3.12 or newer
python3 -m venv .venv
source .venv/bin/activate
pip install httk2           # to include, e.g., VASP support, use: httk2[vasp]
```

</div>
<div class="tab-pane fade" id="install-uv" role="tabpanel">

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install httk2        # to include, e.g., VASP support, use: httk2[vasp]
```

</div>
<div class="tab-pane fade" id="install-conda" role="tabpanel">

```bash
conda create -n httk2 python=3.12 pip
conda activate httk2
python -m pip install httk2
```

</div>
<div class="tab-pane fade" id="install-git-venv" role="tabpanel">

```bash
python3 --version         # check that you have Python 3.12 or newer; otherwise go with git+conda instead
git clone 'https://github.com/httk/httk2.git'
cd httk2
python3 -m venv .venv
source .venv/bin/activate
make checkout-main        # or `make checkout-develop` if you want the unstable develop branch
make install              # or, e.g., `make install-vasp` to also get support for that software
```
If you intend to do httk2 development, also consider:
```bash
make ssh-push-remotes     # makes the httk module repositories push:able via ssh
make install-develop      # adds development tools and util dependencies to your virtual environment
```

</div>
<div class="tab-pane fade" id="install-git-conda" role="tabpanel">

```bash
conda create -n httk2 python=3.12 pip
conda activate httk2
git clone 'https://github.com/httk/httk2.git'
cd httk2
make checkout-main        # or `make checkout-develop` if you want the unstable develop branch
make install              # or, e.g., `make install-vasp` to also get support for that software
```
If you intend to do httk2 development, also consider:
```bash
make ssh-push-remotes     # makes the httk module repositories push:able via ssh
make install-develop      # adds development tools and util dependencies to your virtual environment
```

</div>
</div>

## Quickstart

* A few short general *httk₂* code examples follow in sections below.

* Quickstarts covering specific functionalities are available for working with:

    - [Atomic structures (i.e., crystal structures / slabs / molecules)](quickstart-structures.html)
    - [Vectors](quickstart-vectors.html)
    - [Databases](quickstart-databases.html)
    - [The OPTIMADE client](quickstart-optimade.html)
    - [UI and websites](quickstart-httk-serve.html)
    - [Running calculations and serving the results over OPTIMADE](quickstart-calculations.html)

## Usage overview

<img src="img/httk_maps2.svg" width="100%"/>

Figure showing how *httk₂* spans the central features for true database-centric workflows for high-throughput computations and AI/ML along with API access to data.
Database-centric high-throughput methodology was pioneered by G. Ceder and others in what become the [materials project](https://www.materialsproject.com) See: [[*Commentary: The Materials Project: A materials genome approach to accelerating materials innovation*, A. Jain, G. Hautier, C. J. Moore, S. P. Ong, C. C. Fischer, T. Mueller, K. A. Persson, G. Ceder, Comp. Mat. Sci. 50, 2295 (2011)]](https://doi.org/10.1063/1.4812323).

## A few basic usage examples

### Load a structure file

With *httk-atomistic* installed, `httk.core.load` loads CIF,
POSCAR, and CONTCAR files (including compressed variants such as
`CONTCAR.bz2`) directly into httk₂ structure objects:

```python
from httk.core import load

structure = load("example.cif")

print("Formula:", structure.formula)
print("Volume:", float(structure.cell.volume))

```
A CIF loads as an `ASUStructure` (the file's native symmetry representation);
POSCAR/CONTCAR load as a `UnitcellStructure`. Converting between
representations is done by constructing a view, e.g.
`UnitcellStructureView(structure)` for the full expanded cell.

### Create structures in code

In *httk₂*, a `UnitcellStructure` is created from an explicit cell, a list of
sites in reduced coordinates, and a per-site list of species. Coordinates given
as strings, such as `"1/2"` or `"5.64"`, are kept **exact,** *httk₂* does
all structure algebra in exact arithmetic. Here is a conventional cubic
rock-salt (NaCl) cell:

```python
from httk.atomistic import UnitcellStructure

structure = UnitcellStructure(
    cell=[["5.64", 0, 0], [0, "5.64", 0], [0, 0, "5.64"]],
    sites=[
        [0, 0, 0], ["1/2", "1/2", 0], ["1/2", 0, "1/2"], [0, "1/2", "1/2"],
        ["1/2", "1/2", "1/2"], [0, 0, "1/2"], [0, "1/2", 0], ["1/2", 0, 0],
    ],
    species_at_sites=["Na", "Na", "Na", "Na", "Cl", "Cl", "Cl", "Cl"],
)

print("Formula:", structure.formula)
print("Species:", [s.name for s in structure.species])
print("Number of sites:", len(structure.sites))
print("Volume:", structure.cell.volume, "=", float(structure.cell.volume))

```
Running this generates the output:
```
Formula: ClNa
Species: ['Na', 'Cl']
Number of sites: 8
Volume: (2803221/15625) = 179.406144

```
See the [structures quickstart](quickstart-structures.html) for saving,
supercells, and interoperability with ASE and pymatgen.

### Databases

*httk-store* provides relational storage and querying over SQLite and DuckDB.
Structures — and your own frozen dataclasses — are stored exactly and can be
queried back:

```python
from httk.atomistic import StructureEntry, UnitcellStructureRecord
from httk.store import EntryIdScheme, SqliteStore

store = SqliteStore(
    "example.sqlite",
    entry_records={StructureEntry: UnitcellStructureRecord},
    entry_ids=EntryIdScheme("example", "structures"),
)
sid = store.save(structure)

```
See the [databases quickstart](quickstart-databases.html) and the
[database documentation](https://docs.httk.org/httk-store/).

### Query materials databases over OPTIMADE

The same query interface reaches remote databases that speak the
[OPTIMADE](https://www.optimade.org/) API:

```python
from httk.store.optimade import OptimadeStore

with OptimadeStore("https://alexandria.icams.rub.de/pbe") as store:
    search = store.searcher()
    s = search.variable(store.entry_type("structures"))
    search.add(s.elements.has("Na") & s.elements.has("Cl") & (s.nelements == 2))
    print("Matching structures:", search.count())

```
See the [OPTIMADE client quickstart](quickstart-optimade.html).

## Reporting bugs

Please file bugs at the issue tracker of the relevant module repository within the *httk₂* GitHub organization (please search first to check if it is already reported):

* [https://github.com/httk](https://github.com/httk)

## Citing *httk₂* in scientific works

This is presently the preferred citation:

- Armiento R. (2020) Database-Driven High-Throughput Calculations and Machine Learning Models for Materials Design. In: Schütt K., Chmiela S., von Lilienfeld O., Tkatchenko A., Tsuda K., Müller KR. (eds) Machine Learning Meets Quantum Physics. Lecture Notes in Physics, vol 968. Springer, Cham. [https://doi.org/10.1007/978-3-030-40245-7_17](https://doi.org/10.1007/978-3-030-40245-7_17)

Since *httk₂* may call upon many other pieces of software quite transparently, it may not be initially obvious what other software should be cited. However, *httk₂* keeps track of the functionality your program actually used and can print the corresponding citation list on request. Ask for it at the end of your program, or when it produces a report:

```python
import httk.core

print(httk.core.credits)
```

The output lists what the running program ought to cite and why, including the *httk₂* reference above and the references registered by the modules and external programs that were used. See the [credits documentation](https://docs.httk.org/httk-core/dev/main/credits.html) for details, including how to register citations for your own modules.

**Typography**

When referencing *httk* in digital and printed works, we prefer it to be set in all lowercase italics, and, in particular if version 2 is being referenced, it should be followed by a subscript 2, preferably rendered as an italicized unicode character 2082, i.e., like this: *httk₂*.

<h2 id="contribute">Contribute</h2>

Contributions are very welcome. We are happy to accept issues and pull
requests to the respective `httk-<module>` repositories in the
[httk GitHub organization](https://github.com/httk).

The `httk2` metapackage repository doubles as a development helper
environment: clone it and use its Makefile targets to check out all module
repositories and install them into a virtual environment in one step:

```bash
git clone https://github.com/httk/httk2.git

```
See [Developing *httk₂*](https://github.com/httk/httk2#developing-httk) in the httk2 README for the details.

## More documentation

More extensive documentation about *httk₂* is available at [https://docs.httk.org](https://docs.httk.org)
