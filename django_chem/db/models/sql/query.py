from django.db import connections
from django.db.models.query import sql

from django_chem.db.models.fields import ChemField
from django_chem.db.models.sql.where import ChemWhereNode

# Extend the valid query terms with chem specific ones.
ALL_TERMS = dict([(x, None) for x in (
            'contained', 'matches',
            )])
ALL_TERMS.update(sql.constants.QUERY_TERMS)

class ChemQuery(sql.Query):
    """
    A single chemical SQL query.
    """
    # Overridding the valid query terms.
    query_terms = ALL_TERMS

    compiler = 'ChemSQLCompiler'

    #### Methods overridden from the base Query class ####
    def __init__(self, model, where=ChemWhereNode):
        super(ChemQuery, self).__init__(model, where)
        self.custom_select = {}
        self.extra_select_fields = {}

    def clone(self, *args, **kwargs):
        obj = super(ChemQuery, self).clone(*args, **kwargs)
        # Customized selection dictionary have to also be added to obj.
        obj.custom_select = self.custom_select.copy()
        obj.extra_select_fields = self.extra_select_fields.copy()
        return obj


