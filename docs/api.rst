Database API
============

The objects manager
-------------------

.. module:: django_chem.db.models.manager

.. class:: ChemManager ()

   In order to support chemistry-aware lookup operations, models must override 
   the default object manager. In particular this is true both for models 
   directly aggregating chemical fields (e.g. ``MoleculeField``) and models 
   that are related to chemical fields through foreign keys. Overriding the 
   objects manager simply consists in a reassignment::
   
       from django_chem.db import models
       
       class ChemModel(model.Model):
           # [...]
       	   objects = models.ChemManager()
       
Chemical fields
---------------
   
.. module:: django_chem.db.models.fields

.. class:: MoleculeField ([verbose_name=None, chem_index=False, **options])

   The ``MoleculeField`` represents the structure of a *small* molecule. The 
   actual associated data type is currently defined by the only available 
   backend (i.e. postgresql-rdkit) and consists in a SMILES string.
   
   This field supports some special lookup operations that allow performing
   chemical queries::

       In [1]: from chembldb.models import Compound 

       In [2]: Compound.objects.filter(smiles__contains='c1ccncc1').count()
       Out[2]: 7720
       
       In [3]: Compound.objects.filter(smiles__matches='c1ccacc1').count()
       Out[3]: 42469
       
       In [4]:
   
   In the examples above ``contains`` and ``matches`` select the the structures
   containing the given fragment. ``contains`` expects a SMILES string as 
   input, while ``matches`` supports searches based on SMARTS strings (this 
   makes it more flexible, but also potentially much slower).
   
   In addition, ``exact`` selects structures based on their chemical identity::
   
       In [14]: Compound.objects.filter(smiles__exact='Cc1ccccc1')
       Out[14]: [<Compound: (CHEMBL9113) Cc1ccccc1>]
       
       In [15]:
   
   and ``contained`` searches for structures that are substructures of the 
   given SMILES input (in other words, it's basically the inverse operation
   of ``contains``)::

       In [13]: for c in Compound.objects.filter(smiles__contained='Cc1ccccc1C'):
       ....:     print c
       ....:     
       ....:     
       (CHEMBL9113) Cc1ccccc1
       (CHEMBL17564) C
       (CHEMBL45005) Cc1ccccc1C
       
       In [14]:

Molecular descriptor fields
---------------------------

Some special, non-editable, *molecular descriptor* fields may be associated to 
a ``MoleculeField`` in the same model. The value of these descriptor fields is 
based on the chemical structure stored in the ``MoleculeField`` and it is 
automatically computed by the database backend.

Descriptor fields are associated to the ``MoleculeField`` by name::

    from django_chem.db import models
    
    class Compound(models.Model):
        smiles = models.MoleculeField(chem_index=True)
        mw = models.MolecularWeightField('smiles', db_index=True)

and their values become available once the model instance is saved/updated::

    In [15]: caffeine = Compound(smiles='CN1C=NC2=C1C(=O)N(C(=O)N2C)C')
    
    In [16]: caffeine.mw # no output expected here, no value is yet available
    
    In [17]: caffeine.save()
    
    In [18]: caffeine.mw
    Out[18]: 194.19399999999999
    
    In [19]: 

The following descriptor fields are currently available (please note that the
exact definition of the associated numerical quantity depends on the database
backend):

.. class:: MolecularWeightField (molecule[, **options])

   Molecular weight

.. class:: LogpField (molecule[, **options])

   Estimated logp

.. class:: NumberOfAtomsField (molecule[, **options])

   Number of atoms in the molecular structure

.. class:: NumberOfHeavyAtomsField (molecule[, **options])

   Number of heavy atoms

.. class:: NumberOfHbaField (molecule[, **options])

   Number of hydrogen-bond acceptors

.. class:: NumberOfHbdField (molecule[, **options])

   Number of hydrogen-bond donors

