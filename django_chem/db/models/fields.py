from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import *
from django.db.models.sql.expressions import SQLEvaluator

class ChemField(Field):
    pass

class MoleculeField(ChemField):
    "The Molecule data type -- represents the chemical structure of a compound"

    description = _('Molecule (stored as a canonical-maybe SMILES string)')

    def __init__(self, verbose_name=None, chem_index=False, **kwargs):
        """
        The initialization function for Molecule fields.  Takes the following
        as keyword arguments:

        chem_index:
         Indicates whether to create a structural index. Defaults to False.

        """

        # Setting the index flag with the value of the `chem_index` keyword.
        self.chem_index = chem_index

        # Setting the verbose_name keyword argument with the positional
        # first parameter, so this works like normal fields.
        kwargs['verbose_name'] = verbose_name

        super(MoleculeField, self).__init__(**kwargs)

    def db_type(self, connection):
        return connection.ops.chem_db_type('MoleculeField')

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        """
        Prepare for the database lookup, and return any parameters
        necessary for the query. 
        """
        if lookup_type in connection.ops.chem_terms:
            # special case for isnull lookup
            if lookup_type == 'isnull':
                return []
            # let's try a minimal approach for now
            elif isinstance(value, (tuple, list)):
                return value
            else:
                return [value,]

            # but the following is the more sophisticated version from geodjango

            # Populating the parameters list
            # , and wrapping the Geometry
            # with the Adapter of the spatial backend. (what's this?)
            if isinstance(value, (tuple, list)):
                params = [connection.ops.Adapter(value[0])]
                if 0: #lookup_type in connection.ops.distance_functions:
                    # Getting the distance parameter in the units of the field.
                    params += self.get_distance(value[1:], lookup_type, connection)
                elif 0: #lookup_type in connection.ops.truncate_params:
                    # Lookup is one where SQL parameters aren't needed from the
                    # given lookup value.
                    pass
                else:
                    params += value[1:]
            elif isinstance(value, SQLEvaluator):
                params = []
            else:
                params = [connection.ops.Adapter(value)]

            return params
        else:
            raise ValueError('%s is not a valid chem lookup for %s.' %
                             (lookup_type, self.__class__.__name__))

    def get_prep_lookup(self, lookup_type, value):
        "Perform preliminary non-db specific lookup checks and conversions"
        if lookup_type in (
            'contained', 'contains', 'exact', 'matches',
            ):
            return value

        raise TypeError("Field has invalid lookup: %s" % lookup_type)
    
class FingerprintField(ChemField):
    pass

class BitmapFingerprintField(FingerprintField):
    pass

class SparseFingerprintField(FingerprintField):
    pass

