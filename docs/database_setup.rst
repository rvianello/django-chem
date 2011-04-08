Database setup
==============

Depending on the database backend, some configuration steps may be required before executing a `manage.py syncdb` or being able to create a chemical database.

postgresql-rdkit
----------------

The RDKit extension for PostgreSQL must be installed. Please refer to the `RDKit wiki <http://code.google.com/p/rdkit/wiki/BuildingTheCartridge>`_ for detailed instructions.

creation of a chemical database template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # Creating the template database.
    $ createdb -E UTF8 template_rdkit
    # Allows non-superusers the ability to create from this template
    $ psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_rdkit';"
    # Loading the RDKit cartridge
    $ psql -d template_rdkit -f `pg_config --sharedir`/contrib/rdkit.sql

creation of the database
^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ createdb -T template_rdkit my_chem_db

chemicalite
-----------

Two SQLite extensions library must be available on the system. Moreover, both
the installed SQLite library and pysqlite module must be compiled with support
for loading C extensions at run-time (often turned-off by default for security
reasons).

pysqlite
^^^^^^^^

pysqlite 2.5+ is required and must be compiled with support for dynamic 
loading of C extension. This is most easily accomplished when operating in a
sandboxed environment (e.g. virtualenv)

Unpack the pysqlite sources in a temporary location:

::

    $ mkdir pysqlite && cd pysqlite
    $ wget http://pysqlite.googlecode.com/files/pysqlite-2.6.0.tar.gz
    $ tar zxvf pysqlite-2.6.0.tar.gz
    $ cd pysqlite-2.6.0

Edit the `setup.cfg` file and comment-out the line that disables extensions
loading (the last one in this case; also fix the include and library paths, in
case your SQLite installation is not available in standard locations):

::

    [build_ext]
    #define=
    #include_dirs=/usr/local/include
    #library_dirs=/usr/local/lib
    libraries=sqlite3
    #define=SQLITE_OMIT_LOAD_EXTENSION

Build and install:

::

    $ python setup.py install

Test:

::

    $ cd <somewhere out of the build dir>
    $ python
    [...]
    >>> from pysqlite2 import test
    >>> test.test()
    [...]
    Ran 213 tests in 1.616s
    
    OK
    >>> 

