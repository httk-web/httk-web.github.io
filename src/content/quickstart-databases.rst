:Title: Front page
:Date: 2018-08-16
:Version: 1
:Author: Rickard Armiento
:Template: default
:Base_template: base_default

============================
*httk* quickstart: databases
============================

Create database file, store a structure in it, and retrive it
-------------------------------------------------------------

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
--------------------------------------------------
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

