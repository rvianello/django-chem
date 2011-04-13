from django.db.backends.sqlite3.base import DatabaseOperations
from django_chem.db.backends.base import BaseChemOperations
from django_chem.db.backends.util import ChemOperation, ChemFunction

class ChemicaLiteOperator(ChemOperation):
    "For ChemicaLite operators (e.g. `&&`, `~`)."
    def __init__(self, operator):
        super(ChemicaLiteOperator, self).__init__(operator=operator)

class ChemicaLiteFunction(ChemFunction):
    "For ChemicaLite function calls."
    def __init__(self, function, **kwargs):
        super(ChemicaLiteFunction, self).__init__(function, **kwargs)

class ChemicaLiteOperations(DatabaseOperations, BaseChemOperations):
    
    chemicalite = True

    compiler_module = 'django_chem.db.models.sql.compiler'

    select = 'mol_smiles(%s)'

    def __init__(self, connection):
        super(DatabaseOperations, self).__init__()
        self.connection = connection

        self.structure_operators = {
            # This is from postgresql_rdkit, leave empty for now
            #    'contains'  : (RDKitOperator('@>'), '%s::mol'),
            #    'contained' : (RDKitOperator('<@'), '%s::mol'),
            #    'exact'     : (RDKitOperator('@='), '%s::mol'),
            #    'matches'   : (RDKitOperator('@>'), '%s::qmol'),
            }

        # Creating a dictionary lookup of all chem terms for the RDKit backend.
        chem_terms = ['isnull']
        chem_terms += self.structure_operators.keys()
        self.chem_terms = dict([(term, None) for term in chem_terms])
        
    def chem_db_type(self, field_name):
        try:
            return {
                'MoleculeField':     'molecule',
                }[field_name]
        except KeyError:
            raise NotImplementedError('%s is not implemented for this backend.' 
                                      % field_name)

    def get_chem_placeholder(self, value, field):
        if field.get_internal_type() == 'MoleculeField' and value is not None:
            placeholder = 'mol(%s)'
            if hasattr(value, 'expression'):
                # No chem value used for F expression, substitute in
                # the column name instead.
                return ( placeholder % '%s.%s' % 
                         tuple(map(self.quote_name, 
                                   value.cols[value.expression])) )
            else:
                return placeholder
        else:
            return '%s'

    # note: This was the corresponding method in spatialite
    #
    #def geo_db_type(self, f):
    #    """
    #    Returns None because geometry columnas are added via the
    #    `AddGeometryColumn` stored procedure on SpatiaLite.
    #    """
    #    return None

    def chem_lookup_sql(self, lvalue, lookup_type, value, field, qn):
        """
        Returns the ChemicaLite-specific SQL for the given lookup value
        [a tuple of (alias, column, db_type)], lookup type, lookup
        value, the model field, and the quoting function.
        """
        alias, col, db_type = lvalue

        # Getting the quoted field as `geo_col`.
        geo_col = '%s.%s' % (qn(alias), qn(col))

        if lookup_type in self.structure_operators:
            op, chemical = self.structure_operators[lookup_type]
            return op.as_sql(chem_col, chemical)
        elif lookup_type == 'isnull':
            # Handling 'isnull' lookup type
            return "%s IS %sNULL" % (chem_col, (not value and 'NOT ' or ''))

        raise TypeError("Got invalid lookup_type: %s" % repr(lookup_type))

    def chem_field_eval(self, f):
        raise NotImplementedError('Computation of descriptor field not implemented for this chemical backend.')
