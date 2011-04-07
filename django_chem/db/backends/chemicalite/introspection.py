from django.db.backends.sqlite3.introspection import DatabaseIntrospection, FlexibleFieldLookupDict

class ChemFlexibleFieldLookupDict(FlexibleFieldLookupDict):
    """
    Sublcass that includes updates the `base_data_types_reverse` dict
    for chemical field types.
    """
    base_data_types_reverse = FlexibleFieldLookupDict.base_data_types_reverse.copy()
    base_data_types_reverse.update(
        {'molecule' : 'MoleculeField',
         })

class ChemicaLiteIntrospection(DatabaseIntrospection):
    data_types_reverse = ChemFlexibleFieldLookupDict()

