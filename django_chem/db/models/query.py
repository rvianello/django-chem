from django.db import connections
from django.db.models.query import QuerySet
from django.db.models.query import ValuesQuerySet, ValuesListQuerySet

from django_chem.db.models.sql import ChemQuery

class ChemQuerySet(QuerySet):
    "The chemistry-aware QuerySet."

    ### Methods overloaded from QuerySet ###
    def __init__(self, model=None, query=None, using=None):
        super(ChemQuerySet, self).__init__(model=model, query=query, using=using)
        self.query = query or ChemQuery(self.model)

    def values(self, *fields):
        return self._clone(klass=ChemValuesQuerySet, setup=True, _fields=fields)

    def values_list(self, *fields, **kwargs):
        flat = kwargs.pop('flat', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments to values_list: %s'
                    % (kwargs.keys(),))
        if flat and len(fields) > 1:
            raise TypeError("'flat' is not valid when values_list is called with more than one field.")
        return self._clone(klass=ChemValuesListQuerySet, setup=True, flat=flat,
                           _fields=fields)


    ### ChemQuerySet Methods ###
    #def molecular_weight(self, **kwargs):
    #    """
    #    Returns the molecular weight of the chemical structure field in a `molecular_weight` attribute on
    #    each element of this ChemQuerySet.
    #    """
    #    .....

        

class ChemValuesQuerySet(ValuesQuerySet):
    def __init__(self, *args, **kwargs):
        super(ChemValuesQuerySet, self).__init__(*args, **kwargs)

class ChemValuesListQuerySet(ChemValuesQuerySet, ValuesListQuerySet):
    pass
