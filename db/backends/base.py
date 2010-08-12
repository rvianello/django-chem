class BaseChemOperations(object):
    """
    This module holds the base `BaseChemBackend` object, which is
    instantiated by each spatial database backend with the features
    it has.
    """
    # fingerprinting_functions = {} ?
    substructure_operators = {}
    # similarity_operators = {}
    chem_terms = {}

    # Quick booleans for the type of this spatial backend, and
    # an attribute for the spatial database version tuple (if applicable)
    postgresql_rdkit = False

    molecular_weight = False

    # Aggregates

    # Serialization
    chemhash = False
    chemjson = False
    svg = False

    # Constructors
    from_text = False
    from_wkb = False

    # For quoting column values, rather than columns.
    def chem_quote_name(self, name):
        if isinstance(name, unicode):
            name = name.encode('ascii')
        return "'%s'" % name

    # ChemField operations
    def chem_db_type(self, f):
        """
        Returns the database column type for the chemistry field on
        this chemical backend.
        """
        raise NotImplementedError

    # Chemical SQL Construction
    def chemical_aggregate_sql(self, agg):
        raise NotImplementedError('Aggregate support not implemented for this chemical backend.')

    def chem_lookup_sql(self, lvalue, lookup_type, value, field):
        raise NotImplmentedError

