from django.db import connections
from django.db.models.query import sql

from django_chem.db.models.fields import ChemField
from django_chem.db.models.sql.where import ChemWhereNode

ALL_TERMS = dict([(x, None) for x in (
            'contained', 'contains', 'matches',
            # ? 'equals', 'exact',
            'mw_gt', 'mw_gte', 'mw_lt', 'mw_lte',
            )])
ALL_TERMS.update(sql.constants.QUERY_TERMS)

class ChemQuery(sql.Query):
    """
    A single chemical SQL query.
    """
    # Overridding the valid query terms.
    query_terms = ALL_TERMS

    # compiler = 'ChemSQLCompiler' ? maybe we don't need a specialized compiler. not yet.

    #### Methods overridden from the base Query class ####
    def __init__(self, model, where=ChemWhereNode):
        super(ChemQuery, self).__init__(model, where)
        # The following attributes are customized for the ChemQuerySet.
        # The ChemWhereNode class contains backend-specific
        # routines and functions.
        self.custom_select = {}
        self.extra_select_fields = {}

    def clone(self, *args, **kwargs):
        obj = super(ChemQuery, self).clone(*args, **kwargs)
        # Customized selection dictionary have
        # to also be added to obj.
        obj.custom_select = self.custom_select.copy()
        obj.extra_select_fields = self.extra_select_fields.copy()
        return obj

    def convert_values(self, value, field, connection):
        # no conversion (until I get a clue about what should be converted)
        return value

    # Private API utilities, subject to change.

    # useful to ChemQuerySet to check if a chem field is available for the operation
    def _chem_field(self, field_name=None):
        """
        Returns the first Chemistry field encountered; or specified via the
        `field_name` keyword.  The `field_name` may be a string specifying
        the chemistry field on this ChemQuery's model, or a lookup string
        to a chemistry field via a ForeignKey relation.
        """
        if field_name is None:
            # Incrementing until the first chemical field is found.
            for fld in self.model._meta.fields:
                if isinstance(fld, ChemField): return fld
            return False
        else:
            # Otherwise, check by the given field name -- which may be
            # a lookup to a _related_ chemistry field.
            return ChemWhereNode._check_chem_field(self.model._meta, field_name)
