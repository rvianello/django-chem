# Want to get everything from the 'normal' models package.
from django.db.models import *

# The chemistry-enabled fields.
from django_chem.db.models.fields import MoleculeField, MolecularWeightField, LogpField
from django_chem.db.models.fields import NumberOfAtomsField, NumberOfHeavyAtomsField, NumberOfHbaField, NumberOfHbdField 

# The Managers
from django_chem.db.models.manager import ChemManager

