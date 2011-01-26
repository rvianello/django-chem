
class ChemOperation(object):
    """
    Base class for generating chemical SQL.
    """
    sql_template = '%(chem_col)s %(operator)s %(chemical)s'

    def __init__(self, function='', operator='', result='', **kwargs):
        self.function = function
        self.operator = operator
        self.result = result
        self.extra = kwargs

    def as_sql(self, chem_col, chemical='%s'):
        return self.sql_template % self.params(chem_col, chemical)

    def params(self, chem_col, chemical):
        params = {'function' : self.function,
                  'chem_col' : chem_col,
                  'chemical' : chemical,
                  'operator' : self.operator,
                  'result' : self.result,
                  }
        params.update(self.extra)
        return params

class ChemFunction(ChemOperation):
    """
    Base class for generating chemical SQL related to a function.
    """
    sql_template = '%(function)s(%(chem_col)s, %(chemical)s)'

    def __init__(self, func, result='', operator='', **kwargs):
        # Getting the function prefix.
        default = {'function' : func,
                   'operator' : operator,
                   'result' : result
                   }
        kwargs.update(default)
        super(SpatialFunction, self).__init__(**kwargs)

