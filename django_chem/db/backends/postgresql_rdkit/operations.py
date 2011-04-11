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

        self.structure_operators = {
            'contains'  : (RDKitOperator('@>'), '%s::mol'),
            'contained' : (RDKitOperator('<@'), '%s::mol'),
            'exact'     : (RDKitOperator('@='), '%s::mol'),
            'matches'   : (RDKitOperator('@>'), '%s::qmol'),
            }

        # Creating a dictionary lookup of all chem terms for the RDKit backend.
        chem_terms = ['isnull']
        chem_terms += self.structure_operators.keys()
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

        if lookup_type in self.structure_operators:
            # Handling a RDKit operator.
            op, chemical = self.structure_operators[lookup_type]
            return op.as_sql(chem_col, chemical)
        elif lookup_type == 'isnull':
            # Handling 'isnull' lookup type
            return "%s IS %sNULL" % (chem_col, (not value and 'NOT ' or ''))

        raise TypeError("Got invalid lookup_type: %s" % repr(lookup_type))

    def _build_molecular_descriptor_query(self, func):
        cursor = self.connection.cursor()
        sql = 'SELECT %s(%%s::mol)' % func
        def molecular_descriptor_query(molecule):
            # Data retrieval operation - no commit required
            cursor.execute(sql, [molecule])
            return cursor.fetchone()[0]
        return molecular_descriptor_query

    def chem_field_eval(self, f):
        from django_chem.db.models.fields import \
            MolecularWeightField, LogpField, NumberOfAtomsField, \
            NumberOfHeavyAtomsField, NumberOfHbaField, NumberOfHbdField
        
        if isinstance(f, MolecularWeightField):
            return self._build_molecular_descriptor_query('mol_amw')
        if isinstance(f, LogpField):
            return self._build_molecular_descriptor_query('mol_logp')
        if isinstance(f, NumberOfAtomsField):
            return self._build_molecular_descriptor_query('mol_numatoms')
        if isinstance(f, NumberOfHeavyAtomsField):
            return self._build_molecular_descriptor_query('mol_numheavyatoms')
        if isinstance(f, NumberOfHbaField):
            return self._build_molecular_descriptor_query('mol_hba')
        if isinstance(f, NumberOfHbdField):
            return self._build_molecular_descriptor_query('mol_hbd')
        
        raise NotImplementedError('Computation of descriptor field not implemented for this chemical backend.')

