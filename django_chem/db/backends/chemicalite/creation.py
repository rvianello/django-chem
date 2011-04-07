from django.db.backends.sqlite3.creation import DatabaseCreation

class ChemicaLiteCreation(DatabaseCreation):

    def sql_indexes_for_field(self, model, f, style):
        "Return specific index creation SQL for the field."

        from django_chem.db.models.fields import ChemField

        output = super(ChemicaLiteCreation, self).sql_indexes_for_field(model, 
                                                                        f, 
                                                                        style)

        if isinstance(f, ChemField) and f.chem_index:
            qn = self.connection.ops.quote_name
            db_table = model._meta.db_table

            cqn = self.connection.ops.chem_quote_name
            #qn = self.connection.ops.quote_name
            db_table = model._meta.db_table

            output.append(style.SQL_KEYWORD('SELECT ') +
                          style.SQL_TABLE('mol_structural_index') + '(' +
                          style.SQL_TABLE(cqn(db_table)) + ', ' +
                          style.SQL_FIELD(cqn(f.column)) + ');')

        return output


