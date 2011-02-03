from django.db.backends.postgresql_psycopg2.base import DatabaseOperations
from django_chem.db.backends.base import BaseChemOperations
from django_chem.db.backends.util import ChemOperation, ChemFunction

#### Classes used in constructing RDKit chemical SQL ####
class RDKitOperator(ChemOperation):
    "For RDKit operators (e.g. `@>`, `<@`, `#`, `%`, ...)."
    def __init__(self, operator):
        super(RDKitOperator, self).__init__(operator=operator)


class RDKitFunction(ChemFunction):
    "For RDKit function calls (e.g., ``)."
    def __init__(self, function, **kwargs):
        super(RDKitFunction, self).__init__(function, **kwargs)


class RDKitOperations(DatabaseOperations, BaseChemOperations):

    postgresql_rdkit = True

    def __init__(self, connection):
        super(RDKitOperations, self).__init__(connection)

        self.substructure_operators = {
            'contains'  : RDKitOperator('@>'),
            'contained' : RDKitOperator('<@'),
            'exact' : RDKitOperator('@='),
            }

        # Creating a dictionary lookup of all chem terms for the RDKit backend.
        chem_terms = ['isnull']
        chem_terms += self.substructure_operators.keys()
        self.chem_terms = dict([(term, None) for term in chem_terms])

    def chem_db_type(self, field_name):
        try:
            return {
                'MoleculeField':     'mol',
                }[field_name]
        except KeyError:
            raise NotImplementedError('%s is not implemented for this backend.' 
                                      % field_name)

    def chem_lookup_sql(self, lvalue, lookup_type, value, field, qn):
        """
        Constructs chem SQL from the given lookup value tuple a
        (alias, col, db_type), the lookup type string, lookup value, and
        the geometry field.
        """
        alias, col, db_type = lvalue

        # Getting the quoted chemistry column.
        chem_col = '%s.%s' % (qn(alias), qn(col))

        if lookup_type in self.substructure_operators:
            # Handling a RDKit operator.
            op = self.substructure_operators[lookup_type]
            return op.as_sql(chem_col)
        elif lookup_type == 'isnull':
            # Handling 'isnull' lookup type
            return "%s IS %sNULL" % (chem_col, (not value and 'NOT ' or ''))

        raise TypeError("Got invalid lookup_type: %s" % repr(lookup_type))

