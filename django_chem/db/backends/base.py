class BaseChemOperations(object):
    """
    This module holds the base `BaseChemBackend` object, which is
    instantiated by each chemical database backend with the features
    it has.
    """
    # fingerprinting_functions = {} ?
    structure_operators = {}
    # similarity_operators = {}
    chem_terms = {}

    # Quick booleans for the type of this chemical backend
    postgresql_rdkit = False

    molecular_weight = False

    # Aggregates
    # ?

    # Serialization
    # ?

    # Constructors
    # ?

    # ChemField operations
    def chem_db_type(self, f):
        """
        Returns the database column type for the chemistry field on
        this chemical backend.
        """
        raise NotImplementedError

    def chem_field_eval(self, f):
        """
        Returns the calculator function for the given chemical descriptor
        field in this db backend.
        """
        raise NotImplementedError('Computation of chemical descriptor fields not implemented for this chemical backend.')

    # Chemical SQL Construction
    def chemical_aggregate_sql(self, agg):
        raise NotImplementedError('Aggregate support not implemented for this chemical backend.')

    def chem_lookup_sql(self, lvalue, lookup_type, value, field):
        raise NotImplmentedError

