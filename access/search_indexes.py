# from haystack import indexes
# from access.models import Flavor
#
#
# class FlavorIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
#     number = indexes.IntegerField(model_attr='number')
#     prefix = indexes.CharField(model_attr='prefix')
#     name = indexes.CharField(model_attr='name')
#     approved = indexes.BooleanField(model_attr='approved', faceted=True)
#     sold = indexes.BooleanField(model_attr='sold', faceted=True)
#     valid = indexes.BooleanField(model_attr='valid', faceted=True)
#     natart = indexes.CharField(model_attr='natart', faceted=True)
#     applications = indexes.MultiValueField(faceted=True)
#     hazards = indexes.MultiValueField(faceted=True)
#
#     def prepare_applications(self, obj):
#         return [application.application_type.name for application in obj.applications.all()]
#
#     def prepare_hazards(self, obj):
#         return [category.hazard_class.human_readable_name for category in obj.hazard_set.all()]
#
#     def get_model(self):
#         return Flavor






















#from haystack.indexes import *
#from haystack import site
# from access.models import Flavor, Ingredient, ExperimentalLog
#
# class FlavorIndex(SearchIndex):
#     text = CharField(document=True, model_attr='name')
#
#     def get_queryset(self):
#         return Flavor.objects.all()
#
# site.register(Flavor, FlavorIndex)
#
#
# class IngredientIndex(SearchIndex):
#     text = CharField(document=True, use_template=True)
#     memo = CharField(model_attr='description')
#     comments = CharField(model_attr='comments')
#
#     def get_queryset(self):
#         return Ingredient.objects.all()
#
# site.register(Ingredient, IngredientIndex)
#
#
# class ExperimentalLogIndex(SearchIndex):
#     text = CharField(document=True, model_attr='product_name')
#
#     def get_queryset(self):
#         return ExperimentalLog.objects.all()
#
# site.register(ExperimentalLog, ExperimentalLogIndex)


