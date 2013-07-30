#from haystack.indexes import *
#from haystack import site
from access.models import Flavor, Ingredient, ExperimentalLog

class FlavorIndex(SearchIndex):
    text = CharField(document=True, model_attr='name')
    
    def get_queryset(self):
        return Flavor.objects.all()
    
site.register(Flavor, FlavorIndex)


class IngredientIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    memo = CharField(model_attr='description')
    comments = CharField(model_attr='comments')
    
    def get_queryset(self):
        return Ingredient.objects.all()
    
site.register(Ingredient, IngredientIndex)


class ExperimentalLogIndex(SearchIndex):
    text = CharField(document=True, model_attr='product_name')
    
    def get_queryset(self):
        return ExperimentalLog.objects.all()
    
site.register(ExperimentalLog, ExperimentalLogIndex)