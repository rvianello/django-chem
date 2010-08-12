from django.db.backends.postgresql_psycopg2.introspection import DatabaseIntrospection

class ChemIntrospectionError(Exception):
    pass

class RDKitIntrospection(DatabaseIntrospection):
    # Reverse dictionary for RDKit types not populated until
    # introspection is actually performed.
    rdkit_types_reverse = {}

    def get_rdkit_types(self):
        """
        Returns a dictionary with keys that are the PostgreSQL object
        identification integers for the RDKit types.
        """
        cursor = self.connection.cursor()
        # The OID integers associated with the type may
        # be different across versions; hence, this is why we have
        # to query the PostgreSQL pg_type table corresponding to the
        # RDKit custom data types.
        oid_sql = 'SELECT "oid" FROM "pg_type" WHERE "typname" = %s'
        try:
            cursor.execute(oid_sql, ('mol',))
            MOL_TYPE = cursor.fetchone()[0]
            rdkit_types = { MOL_TYPE : 'SmilesField' }
        finally:
            cursor.close()

        return postgis_types

    def get_field_type(self, data_type, description):
        if not self.rdkit_types_reverse:
            self.rdkit_types_reverse = self.get_rdkit_types()
            self.data_types_reverse.update(self.rdkit_types_reverse)
        return super(RDKitIntrospection, self).get_field_type(data_type, description)
