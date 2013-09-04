from django.db.models import Q

class ArtNatiFilter():
    label = "Natural/Artificial"
    key_string = "checked_boxes[art_nati][]"
    
    @staticmethod
    def get_q_list(checked_boxes):
        q_list = [Q(art_nati__iexact = art_nati_filter) for art_nati_filter in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
class Prop65Filter():
    label = "Prop65"
    key_string = "checked_boxes[prop65][]"
    
    @staticmethod
    def get_q_list(checked_boxes):
        q_list = [Q(prop65__iexact = prop65_filter) for prop65_filter in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
#class AllergenExcludeFilter():
#    label = "Allergen"
    