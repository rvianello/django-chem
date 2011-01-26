from django.db.models.manager import Manager
from django_chem.db.models.query import ChemQuerySet

class ChemManager(Manager):
    "Overrides Manager to return chemistry-aware QuerySets."
    
    # the purpose of this custom manager is to return and manipulate
    # these customized querysets which are capable of chemically aware
    # operations (on the correct field types, of course).
    
    # we therefore override get_query_set() and forward to it all calls that
    # are not supported by the manager.

    # we promise no object will be filtered out by default and we'll make our
    # best to make this manager such that can be used as a default manager
    use_for_related_fields = True

    # use a custom queryset
    def get_query_set(self):
        return ChemQuerySet(self.model, using=self._db)

    # forward to the custom queryset all the operation it supports and
    # user will call on the manager too
    #
    # def some_method(self, *args, **kwargs):
    #     return self.get_query_set().some_method(*args, **kwargs)
