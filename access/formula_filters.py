from django.db.models import Q

class ArtNatiFilter():
    label = "Natural/Artificial"
    key_string = "checked_boxes[art_nati][]"
    exclude = False
    
    @staticmethod
    def get_q_list(checked_boxes):
        q_list = [Q(art_nati__iexact = art_nati_filter) for art_nati_filter in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
class Prop65Filter():
    label = "Prop65"
    key_string = "checked_boxes[prop65][]"
    exclude = False
    
    @staticmethod
    def get_q_list(checked_boxes):
        q_list = [Q(prop65__iexact = prop65_filter) for prop65_filter in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
class AllergenExcludeFilter():
    label = "Allergens"
    key_string = "checked_boxes[allergen][]"
    exclude = True
   
    @staticmethod
    def get_q_list(checked_boxes):
        q_list = [Q(allergen__contains = allergen_exclusion) for allergen_exclusion in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
'''    
class PropertyExclude():
    def get_q_list(checked_boxes):
        exclude_list = ['gmo', 'prop65']
        q_list = [Q(exclude_prop__icontains = 'no') for exclude_prop in exclude_list]
'''    
# excludelist = diacetyl, nopg, gmo, prop65
# q_list = [Q(property__icontains = 'no','none') for property in excludelist
    