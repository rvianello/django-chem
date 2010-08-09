from django.db.backends.postgresql_psycopg2.base import *
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper as Psycopg2DatabaseWrapper
from django_chem.db.backends.postgresql_rdkit.creation import RDKitCreation
#from django.contrib.gis.db.backends.postgis.introspection import PostGISIntrospection
from django_chem.db.backends.postgresql_rdkit.operations import RDKitOperations

class DatabaseWrapper(Psycopg2DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.creation = RDKitCreation(self)
        self.ops = RDKitOperations(self)
        #self.introspection = PostGISIntrospection(self)
