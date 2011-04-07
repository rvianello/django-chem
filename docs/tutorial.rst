Tutorial
========

*** * * IN PROGRESS (this document is not complete and is likely to contain errors) * * ***

This tutorial is based on a similar document available from the `RDKit wiki <http://code.google.com/p/rdkit/wiki/DatabaseCreation>`_. The Python bindings to the RDKit libraries will be used in some data processing steps, so you'll need to have them available on your system. 

Create a django project::

    $ django-admin startproject chembldb_tutorial
    $ cd chembldb_tutorial

And create a django application to manage the tutorial data::

    $ ./manage.py startapp chembldb

Edit ``chembldb_tutorial/chembldb/models.py`` to define the data model::

    # please note that model are imported from django_chem.db
    # instead of django.db (as one would usually do)
    from django_chem.db import models
    
    class Compound(models.Model):
    
        # chembl_id is an ordinary django CharField
        chembl_id = models.CharField(max_length=20, db_index=True)
    
        # smiles is a MoleculeField from django_chem
        # chem_index=True is required if the application performs
        # structural searches
        smiles = models.MoleculeField(chem_index=True)
        
        # models using fields from django_chem (or referring them
        # through extermal keys) must override the default object 
        # manager
        objects = models.ChemManager()
        
        def __unicode__(self):
            return u'(%s) %s' % (self.chembl_id, self.smiles)
        

Edit the file ``chembldb_tutorial/settings.py`` to define the database that will
be used in this tutorial and to install the chembldb application::

    DATABASES = {
        'default': {
            'ENGINE': 'django_chem.db.backends.postgresql_rdkit',
            'NAME': 'chembldb_tutorial', 
            'USER': 'django',      # fix this to match your postgresql user
            'PASSWORD': 'django',  # fix this too
            'HOST': '',  # Set to empty string for localhost.
            'PORT': '',  # Set to empty string for default.
        }
    }
    
    # [...]

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        # Uncomment the next line to enable the admin:
        # 'django.contrib.admin',
        'chembldb',
    )

Now create the database::

    $ createdb -Udjango -Ttemplate_rdkit chembldb_tutorial
    $ ./manage.py syncdb

Download the `ChEMBLdb <https://www.ebi.ac.uk/chembldb/index.php>`_ database and decompress it::

    $ wget ftp://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_08/chembl_08_chemreps.txt.gz
    $ gunzip chembl_08_chemreps.txt.gz

The data is formatted as a csv file, tab-separated and beginning with a header line::

    $ head -n3  chembl_08_chemreps.txt 
    chembl_id	chebi_id	molweight	canonical_smiles	inchi	inchi_key
     CHEMBL6582	100733	268.09877	NC(=O)c1cc(nnc1Cl)c2ccc(Cl)cc2	InChI=1/C11H7Cl2N3 <snip>
     CHEMBL6583	100744	342.41542	CN(C)c1cccc2c(cccc12)S(=O)(=O)Nc3cnc(C)cn3	In <snip>

In this tutorial only a subset of this data will be used, and at the same time we want to make sure that troublesome SMILES strings are skipped (SMILES containing errors, compounds that are too big and/or other strings that the RDKit cartridge won't be able to process). File parsing and data filtering can be performed with a function similar to the following::

    def read_chembldb(filepath, limit=0):
        import csv 
        from rdkit import Chem
    
        count = 0
        inputfile = open(filepath, 'rb')
        reader = csv.reader(inputfile, delimiter='\t', skipinitialspace=True)
        reader.next() # skip header line
    
        for chembl_id, chebi_id, mw, smiles, inchi, inchi_key in reader:
    
            # skip problematic compounds
            if len(smiles) > 300: continue
            smiles = smiles.replace('=N#N','=[N+]=[N-]')
            smiles = smiles.replace('N#N=','[N-]=[N+]=')
            if not Chem.MolFromSmiles(smiles): continue
    
            yield chembl_id, smiles
    
            count +=1
            if limit > 0 and count == limit: break

To import the data we will directly access the Django ORM api. Start the django management shell::

    $ ./manage.py shell

and import the ``Compound`` database model::

    In [1]: from chembldb.models import Compound

with this model class and the ``read_chembldb`` function above, importing the compounds only takes a simple loop *(please note that importing the whole database may require a few hours; to keep this tutorial short we'll limit this operation to the first 25K compounds)*::

    In [3]: for chembl_id, smiles in read_chembldb('./chembl_08_chemreps.txt', 25000):
       ...:     c = Compound(chembl_id=chembl_id, smiles=smiles)
       ...:     c.save()
       ...:     
       ...:     

and we can finally perform some queries. We can for example verify the number of compounds in the database::

    In [4]: Compound.objects.count()
    Out[4]: 25000

or display the first 5 compounds::

    In [6]: for c in Compound.objects.all()[:5]: print c
       ...: 
    (CHEMBL6582) NC(=O)c1cc(-c2ccc(Cl)cc2)nnc1Cl
    (CHEMBL6583) Cc1cnc(NS(c2cccc3c(N(C)C)cccc23)(=O)=O)cn1
    (CHEMBL6584) CN(C)/C=N/c1nc(/N=C\N(C)C)c2c(ncc(Sc3cc(Cl)c(Cl)cc3)n2)n1
    (CHEMBL6585) CC12C(C[C@@H](I)[C@@H]1O)C1C(c3ccc(O)cc3CC1)CC2
    (CHEMBL6637) C/C(=C\Cn1oc(=O)[nH]c1=O)c1ccc(OCCc2nc(-c3ccc(C(F)(F)F)cc3)oc2C)cc1

Finally (and hopefully more interestingly), here's a first example of a chemical query, searching the database for a given substructure::

    In [12]: # which compounds contain 'c1cccc2c1nncc2' as a substructure?
    
    In [13]: for c in Compound.objects.filter(smiles__contains='c1cccc2c1nncc2'): print c
       ....: 
    (CHEMBL12112) CC(C)Sc1ccc(CC2CCN(C3CCN(C(=O)c4cnnc5ccccc54)CC3)CC2)cc1
    (CHEMBL26025) Cc1cccc(NC(=O)Nc2ccc3nnccc3c2)c1
