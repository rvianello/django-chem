from django.db.models.fields import Field, FieldDoesNotExist
from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models.sql.expressions import SQLEvaluator
from django.db.models.sql.where import Constraint, WhereNode
from django_chem.db.models.fields import ChemField

class ChemConstraint(Constraint):
    """
    This subclass overrides `process` to better handle chemical SQL
    construction.
    """
    def __init__(self, init_constraint):
        self.alias = init_constraint.alias
        self.col = init_constraint.col
        self.field = init_constraint.field

    def process(self, lookup_type, value, connection):
        if isinstance(value, SQLEvaluator):
            # Make sure the F Expression destination field exists
            chem_fld = ChemWhereNode._check_chem_field(value.opts, value.expression.name)
            if not chem_fld:
                raise ValueError('No chemistry field found in expression.')
        db_type = self.field.db_type(connection=connection)
        params = self.field.get_db_prep_lookup(lookup_type, value, connection=connection)
        return (self.alias, self.col, db_type), params

class ChemWhereNode(WhereNode):
    """
    Used to represent the SQL where-clause for spatial databases --
    these are tied to the ChemQuery class that created it.
    """
    def add(self, data, connector):
        if isinstance(data, (list, tuple)):
            obj, lookup_type, value = data
            if ( isinstance(obj, Constraint) and
                 isinstance(obj.field, ChemField) ):
                data = (ChemConstraint(obj), lookup_type, value)
        super(ChemWhereNode, self).add(data, connector)

    def make_atom(self, child, qn, connection):
        lvalue, lookup_type, value_annot, params_or_value = child
        if isinstance(lvalue, ChemConstraint):
            data, params = lvalue.process(lookup_type, params_or_value, connection)
            # delegate the chem-specific sql to the backend
            chemical_sql = connection.ops.chemical_lookup_sql(data, lookup_type, 
                                                              params_or_value, lvalue.field, qn)
            return chemical_sql, params
        else:
            return super(ChemWhereNode, self).make_atom(child, qn, connection)

    @classmethod
    def _check_chem_field(cls, opts, lookup):
        """
        Utility for checking the given lookup with the given model options.
        The lookup is a string either specifying the chemistry field, or a related 
        lookup on a chemistry field like 'substrate__structure'.

        If a ChemField exists according to the given lookup on the model
        options, it will be returned.  Otherwise returns None.
        """
        # This takes into account the situation where the lookup is a
        # lookup to a related chemistry field like 'substrate__structure'.
        field_list = lookup.split(LOOKUP_SEP)

        # Reversing so list operates like a queue of related lookups,
        # and popping the top lookup.
        field_list.reverse()
        fld_name = field_list.pop()

        try:
            chem_fld = opts.get_field(fld_name)
            # If the field list is still around, then it means that the
            # lookup was for a chem field across a relationship --
            # thus we keep on getting the related model options and the
            # model field associated with the next field in the list
            # until there's no more left.
            while len(field_list):
                opts = chem_fld.rel.to._meta
                chem_fld = opts.get_field(field_list.pop())
        except (FieldDoesNotExist, AttributeError):
            return False

        # Finally, make sure we got a Chem field and return.
        if isinstance(chem_fld, ChemField):
            return chem_fld
        else:
            return False
