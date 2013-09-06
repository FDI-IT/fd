from django.db.models import Q

from access.models import Ingredient

class ArtNatiFilter():
    label = "Natural/Artificial"
    key_string = "checked_boxes[art_nati][]"
    exclude = False
    
    @staticmethod
    def get_query_object(checked_boxes):
        q_list = [Q(art_nati__iexact = art_nati_filter) for art_nati_filter in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
    @staticmethod
    def get_filtered_ingredients(checked_boxes):
        return Ingredient.objects.filter(ArtNatiFilter.get_query_object(checked_boxes))
    
class Prop65Filter():
    label = "Prop65"
    key_string = "checked_boxes[prop65][]"
    exlude = False
    
    @staticmethod
    def get_query_object(checked_boxes):
        q_list = [Q(prop65__iexact = prop65_filter) for prop65_filter in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
class AllergenExcludeFilter():
    label = "Allergen"
    key_string = "checked_boxes[allergen][]"
    exclude = True
   
    @staticmethod
    def get_query_object(checked_boxes):
        print checked_boxes
        q_list = [Q(allergen__contains = allergen_exclusion) for allergen_exclusion in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    