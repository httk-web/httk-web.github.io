:Title: Front page
:Date: 2020-09-27
:Version: 1
:Author: Rickard Armiento
:Template: front
:Base_template: base_default

====================================
The High-Throughput Toolkit (*httk*)
====================================

The High-Throughput Toolkit (*httk*) is a toolkit for preparing and running calculations, analyzing the results, and storing results in global and/or personalized databases. *httk* is presently targeted at atomistic calculations in materials science and electronic structure, but aims to be extended into a library useful also outside those areas.

*httk* was created in 2014.

..
  It is a design guideline of *httk* that its central functionality is implemented in pure Python without external dependencies. However, it does support a number of integrations with other libraries.

  *httk* contains a number of subcomponents written in pure Python that may be useful in other contexts:

  - A general workflow manager that allows running sophisticated ensemble jobs on supercomputers over thousands of CPU cores, just as well as executing multi-stage operations on your own computer.

  - A strong object relational mapper that allow storing general Python objects in an sql database and do queries on them.

  - A deterministic arbitrary precision numerical library with arrays.

  - A UI library based on html and templates that allows using the same Python code for websites and user interfaces.

Installation
------------

* If you just want to use *httk*, this should work:

  .. code:: bash

     pip install httk

  - If your ``pip`` works as it should, you should be able to do ``import httk`` in Python, as well as run the ``httk`` command line tool.

  ..

* An alternative is to clone the master branch of our source code repository, which is meant to always give you the latest release:

  .. code:: bash

       git clone https://github.com/httk/httk

  Then, every time you want to use *httk* you need to initialize the environtment with:

  .. code:: bash

       source /path/to/httk/init.shell

  (Which, of course, can be put in your shell initialization scripts)

* For more installation alternatives, see the `full documentation <https://docs.httk.org/en/latest/>`__.

Quickstart
----------

* A few short general *httk* code examples follow in sections below.

* Quickstarts covering specific functionalities are available for working with:

  - `Atomic structures (i.e., crystal structures / slabs / molecules) <quickstart-structures.html>`__
  - `Vectors <quickstart-vectors.html>`__
  - `UI and websites <quickstart-httkweb.html>`__
  - `Databases <quickstart-databases.html>`__

* The *httk* installation also contains the subdirectories ``Examples`` and ``Tutorial/step1``, ``/step2``, etc.

A few simple usage examples
---------------------------

Load a cif file or poscar
+++++++++++++++++++++++++

This is a very simple example of just loading a structure from a ``.cif`` file and writing out some information about it.

.. code:: python

  import httk

  struct = httk.load("example.cif")

  print("Formula:", struct.formula)
  print("Volume:", float(struct.uc_volume))
  print("Assignments:", struct.uc_formula_symbols)
  print("Counts:", struct.uc_counts )
  print("Coords:", struct.uc_reduced_coords)

Running this generates the output::

  ('Formula:', 'BO2Tl')
  ('Volume', 509.24213999999984)
  ('Assignments',['B', 'O', 'Tl'])
  ('Counts:', [8, 16, 8])
  ('Coords', FracVector(((1350,4550,4250) , ... , ,10000)))

..

Create structures in code
+++++++++++++++++++++++++

.. code:: python

  from httk.atomistic import Structure

  cell = [[1.0, 0.0, 0.0] ,
          [0.0, 1.0, 0.0] ,
          [0.0, 0.0, 1.0]]
  coordgroups = [[
                    [0.5, 0.5, 0.5]
                 ],[
                    [0.0, 0.0, 0.0]
                 ],[
                    [0.5, 0.0, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 0.5]
                 ]]

  assignments = ['Pb' ,'Ti' ,'O']
  volume =62.79
  struct = Structure.create(uc_cell = cell,
               uc_reduced_coordgroups = coordgroups,
               assignments = assignments,
               uc_volume = volume)


Create database file, store a structure in it, and retrive it
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: python

  import httk, httk.db
  from httk.atomistic import Structure

  backend = httk.db.backend.Sqlite('example.sqlite')
  store = httk.db.store.SqlStore(backend)

  tablesalt = httk.load('NaCl.cif')
  store.save(tablesalt)

  arsenic = httk.load('As.cif')
  store.save(arsenic)

  # Search for anything with Na
  search = store.searcher()
  search_struct = search.variable(Structure)
  search.add(search_struct.formula_symbols.is_in('Na'))

  search.output(search_struct, 'structure')

  for match, header in list(search):
      struct = match[0]
      print "Found structure", struct.formula, [str(struct.get_tags()[x]) for x in struct.get_tags()]



Create database file and store your own data in it
++++++++++++++++++++++++++++++++++++++++++++++++++
.. code:: python

  #!/usr/bin/env python

  import httk, httk.db
  from httk.atomistic import Structure

  class StructureIsEdible(httk.HttkObject):

      @httk.httk_typed_init({'structure': Structure, 'is_edible': bool})
      def __init__(self, structure, is_edible):
	  self.structure = structure
	  self.is_edible = is_edible

  backend = httk.db.backend.Sqlite('example.sqlite')
  store = httk.db.store.SqlStore(backend)

  tablesalt = httk.load('NaCl.cif')
  edible = StructureIsEdible(tablesalt, True)
  store.save(edible)

  arsenic = httk.load('As.cif')
  edible = StructureIsEdible(arsenic, False)
  store.save(edible)


Reporting bugs
--------------

Please file bugs at the issue tracker at github (please search first to check if it is already reported):

* https://github.com/rartino/httk/issues

Citing *httk* in scientific works
---------------------------------

This is presently the preferred citation:

- \R. Armiento et al., The High-Throughput Toolkit (httk), http://httk.org/; Armiento R. (2020) Database-Driven High-Throughput Calculations and Machine Learning Models for Materials Design. In: Schütt K., Chmiela S., von Lilienfeld O., Tkatchenko A., Tsuda K., Müller KR. (eds) Machine Learning Meets Quantum Physics. Lecture Notes in Physics, vol 968. Springer, Cham. https://doi.org/10.1007/978-3-030-40245-7_17

Since *httk* may call upon many other pieces of software quite
transparently, it may not be initially obvious what other software
should be cited. Unless configured otherwise, *httk* prints out a list
of citations when the program ends. You should take note of those
citations and include them in your publications if relevant.

More documentation
------------------

More extensive documentation about *httk* is available at https://docs.httk.org

