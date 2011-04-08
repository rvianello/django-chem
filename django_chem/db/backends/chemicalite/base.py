from ctypes.util import find_library
from django.conf import settings

from django.core.exceptions import ImproperlyConfigured
from django.db.backends.sqlite3.base import *
from django.db.backends.sqlite3.base import DatabaseWrapper as \
    SqliteDatabaseWrapper, _sqlite_extract, _sqlite_date_trunc, _sqlite_regexp

from django_chem.db.backends.chemicalite.creation import ChemicaLiteCreation
from django_chem.db.backends.chemicalite.introspection \
    import ChemicaLiteIntrospection
from django_chem.db.backends.chemicalite.operations import ChemicaLiteOperations

class DatabaseWrapper(SqliteDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        # Before we get too far, make sure pysqlite 2.5+ is installed.
        if Database.version_info < (2, 5, 0):
            raise ImproperlyConfigured('Only versions of pysqlite 2.5+ are '
                                       'compatible with ChemicaLite.')

        # Trying to find the location of the ChemicaLite and SignTree 
        # libraries.
        # Here we are figuring out the path to the ChemicaLite libraries
        # (`libsigntree` and `libchemicalite`). 
        # If it's not in the system library path (e.g., it cannot be found 
        # by `ctypes.util.find_library`), then it may be set manually in the 
        # settings via the `SIGNTREE_LIBRARY_PATH` and 
        # `CHEMICALITE_LIBRARY_PATH` settings.
        self.signtree_lib = getattr(settings, 'SIGNTREE_LIBRARY_PATH',
                                    find_library('signtree'))
        if not self.signtree_lib:
            raise ImproperlyConfigured('Unable to locate the SignTree library. '
                                       'Make sure it is in your library path, '
                                       'or set SIGNTREE_LIBRARY_PATH in your '
                                       'settings.'
                                       )
        self.chemicalite_lib = getattr(settings, 'CHEMICALITE_LIBRARY_PATH',
                                       find_library('chemicalite'))
        if not self.chemicalite_lib:
            raise ImproperlyConfigured('Unable to locate the ChemicaLite '
                                       'library. '
                                       'Make sure it is in your library path, '
                                       'or set CHEMICALITE_LIBRARY_PATH in '
                                       'your settings.'
                                       )

        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.ops = ChemicaLiteOperations(self)
        self.creation = ChemicaLiteCreation(self)
        self.introspection = ChemicaLiteIntrospection(self)

    def _cursor(self):
        if self.connection is None:
            ## The following is the same as in django.db.backends.sqlite3.base
            settings_dict = self.settings_dict
            if not settings_dict['NAME']:
                raise ImproperlyConfigured("Please fill out the database NAME "
                                           "in the settings module before "
                                           "using the database.")
            kwargs = {
                'database': settings_dict['NAME'],
                'detect_types': (Database.PARSE_DECLTYPES | 
                                 Database.PARSE_COLNAMES),
            }
            kwargs.update(settings_dict['OPTIONS'])
            self.connection = Database.connect(**kwargs)
            # Register extract, date_trunc, and regexp functions.
            self.connection.create_function("django_extract", 2, 
                                            _sqlite_extract)
            self.connection.create_function("django_date_trunc", 2, 
                                            _sqlite_date_trunc)
            self.connection.create_function("regexp", 2, _sqlite_regexp)
            connection_created.send(sender=self.__class__, connection=self)

            ## From here on, customized for ChemDjango ##

            # Enabling extension loading on the SQLite connection.
            try:
                self.connection.enable_load_extension(True)
            except AttributeError:
                raise ImproperlyConfigured('The pysqlite library does not '
                                           'support C extension loading. '
                                           'Both SQLite and pysqlite must be '
                                           'configured to allow the loading '
                                           'of extensions to use ChemicaLite.'
                                           )

            # Loading the ChemicaLite library extensions on the connection, 
            # and returning the created cursor.
            cur = self.connection.cursor(factory=SQLiteCursorWrapper)
            try:
                cur.execute("SELECT load_extension(%s)", (self.signtree_lib,))
            except Exception, msg:
                raise ImproperlyConfigured('Unable to load the SignTree '
                                           'library extension "%s" because: %s'
                                           % (self.signtree_lib, msg))
            try:
                cur.execute("SELECT load_extension(%s)", 
                            (self.chemicalite_lib,))
            except Exception, msg:
                raise ImproperlyConfigured('Unable to load the ChemicaLite '
                                           'library extension "%s" because: %s' 
                                           % (self.chemicalite_lib, msg))
            return cur
        else:
            return self.connection.cursor(factory=SQLiteCursorWrapper)
