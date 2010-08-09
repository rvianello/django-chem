from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import Field

class SmilesField(Field):
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

        super(SmilesField, self).__init__(**kwargs)

    def db_type(self, connection):
        return connection.creation.chem_db_type('SmilesField')

    
