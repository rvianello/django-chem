from django.db.models.manager import Manager
from django_chem.db.models.query import SmilesQuerySet

class SmilesManager(Manager):
    "Overrides Manager to return SMILES QuerySets."
    
    pass
