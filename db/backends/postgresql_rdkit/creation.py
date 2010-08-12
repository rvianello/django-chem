from django.db.backends.postgresql.creation import DatabaseCreation

class RDKitCreation(DatabaseCreation):

    def sql_indexes_for_field(self, model, f, style):
        "Return specific index creation SQL for the field."

        from django_chem.db.models.fields import ChemField

        output = super(RDKitCreation, self).sql_indexes_for_field(model, 
                                                                  f, style)

        if isinstance(f, ChemField) and f.chem_index:
            qn = self.connection.ops.quote_name
            db_table = model._meta.db_table

            output.append(style.SQL_KEYWORD('CREATE INDEX ') +
                          style.SQL_TABLE(qn('%s_%s_gist_idx' % 
                                             (db_table, f.column))) +
                          style.SQL_KEYWORD(' ON ') +
                          style.SQL_TABLE(qn(db_table)) +
                          style.SQL_KEYWORD(' USING ') +
                          style.SQL_COLTYPE('GIST') + ' ( ' +
                          style.SQL_FIELD(qn(f.column)) + ' );')

        return output
