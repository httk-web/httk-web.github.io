:Title: Front page
:Date: 2018-08-16
:Version: 1
:Author: Rickard Armiento
:Template: default
:Base_template: base_default

=============================
*httk* quickstart: structutes
=============================

Load a cif file or poscar
-------------------------

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
-------------------------

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

