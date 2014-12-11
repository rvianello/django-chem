from django.utils.six import with_metaclass
from django.utils.translation import ugettext_lazy as _
from django.db.models import SubfieldBase
from django.db.models.fields import *

from rdkit import Chem
from rdkit.Chem.rdchem import Mol

class MoleculeField(with_metaclass(SubfieldBase, Field)):

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

    def to_python(self, value):
        # consider setting the SubfieldBase metaclass

        if isinstance(value, Mol):
            return value

        # The string case. 
        value = Chem.MolFromSmiles(value)
        if not value:
            raise ValidationError("Invalid input for a Mol instance")
        return value

    def get_prep_value(self, value):
        # convert the Molecule instance to the value used by the 
        # db driver
        if isinstance(value, Mol):
            return Chem.MolToSmiles(value, isomericSmiles=True, canonical=False)
            
        return value

    # don't reimplement db-specific preparation of query values for now
    # def get_db_prep_value(self, value, connection, prepared=False):
    #    return value

    def get_prep_lookup(self, lookup_type, value):
        "Perform preliminary non-db specific lookup checks and conversions"
        if lookup_type in (
            'contained', 'contains', 'exact', 'matches',
            ):
            return value
        raise TypeError("Field has invalid lookup: %s" % lookup_type)

    # this will be probably needed.
    def get_db_prep_lookup(lookup_type, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_lookup(lookup_type, value)
        return value
