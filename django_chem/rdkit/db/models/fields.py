from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import *

from rdkit.Chem.rdchem import Mol

class MoleculeField(Field):

    description = _("Molecule")

    def __init__(self, verbose_name=None, chem_index=True, *args, **kwargs):
        self.chem_index = chem_index
        kwargs['verbose_name'] = verbose_name
        super(MoleculeField, self).__init__(*args, **kwargs)
    
    def db_type(self, connection):
        return 'mol'
    
    def deconstruct(self):
        name, path, args, kwargs = super(MoleculeField, self).deconstruct()
        # include chem_index if not the default value.
        if self.chem_index is not True:
            kwargs['chem_index'] = self.chem_index
        return name, path, args, kwargs

    """
    def to_python(self, value):
        # consider setting the SubfieldBase metaclass

        if isinstance(value, Mol):
            return value

        # The string case.
        # smiles? ctab?
        raise ValidationError("Invalid input for a Mol instance")
        
        #return a Molecule instantiated from the string

    def get_prep_value(self, value):
        # convert the Molecule instance to the value used by the 
        # db driver

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(BinaryField, self).get_db_prep_value(value, connection, prepared)
        if value is not None:
            return connection.Database.Binary(value)
        return value

    def get_prep_lookup(self, lookup_type, value):
        "Perform preliminary non-db specific lookup checks and conversions"
        if lookup_type in (
            'contained', 'contains', 'exact', 'matches',
            ):
            return value

        raise TypeError("Field has invalid lookup: %s" % lookup_type)


    """
