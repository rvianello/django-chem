Project setup
=============

To use django_chem in a django project you should do the following:

* make it available in the ``PYTHONPATH`` or ``sys.path``
* in your ``settings.py`` file, change the ``ENGINE`` value in the ``DATABASES`` dictionary::

        'ENGINE': 'django_chem.db.backends.postgresql_rdkit',

* models using ``MoleculeField`` type fields need to override the default manager with a ``ChemManager`` instance like this::

        # please note we import from django_chem.db
        from django_chem.db import models
        
        class Molecule(models.Model):
            name = models.CharField(max_length=200, db_index=True)
            m = models.MoleculeField(chem_index=True)
            
            objects = models.ChemManager()
