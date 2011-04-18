from django.db import connections
from django.db.models.query import QuerySet
from django.db.models.query import ValuesQuerySet, ValuesListQuerySet
from django.db.models.query_utils import Q

from django.db.models.sql.constants import LOOKUP_SEP

from django_chem.db.models.sql import ChemQuery

from django_chem.db.models.sql import ChemWhereNode as _ChemWhereNode
from django_chem.db.models import MoleculeField as _MoleculeField

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
    
    def _filter_or_exclude(self, negate, *args, **kwargs):
        if connections[self.db].ops.chemicalite:
            args, kwargs = self._chemicalite_filter(args, kwargs)
        return super(ChemQuerySet, self)._filter_or_exclude(negate, 
                                                            *args, **kwargs)

    def _chemicalite_filter(self, args, original_kwargs):
        chemicalite = connections[self.db].ops
        opts = self.query.get_meta()

        args = list(args)
        kwargs = {}

        for lookup, value in original_kwargs.items():
            parts = lookup.split(LOOKUP_SEP)
            if len(parts) == 1 or parts[-1] not in self.query.query_terms:
                lookup_type = 'exact'
            else:
                lookup_type = parts.pop()
            
            chemfield = _ChemWhereNode._check_chem_field(opts, 
                                                         LOOKUP_SEP.join(parts))

            if ( lookup_type in chemicalite.structure_operators and
                 chemfield and isinstance(chemfield, _MoleculeField) ):
                stridx_attname = chemfield.stridx_attname
                stridx_lookup_type = chemicalite.stridx_lookup[lookup_type]
                stridx_parts = (parts[:-1] + 
                                [stridx_attname, stridx_lookup_type])
                stridx_lookup = LOOKUP_SEP.join(stridx_parts)
                args.extend( (Q(**{lookup: value}), 
                              Q(**{stridx_lookup: value})) )
            else:
                kwargs[lookup] = value
            
        return tuple(args), kwargs

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
