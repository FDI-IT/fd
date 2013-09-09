from django.db.models import Q

from access.models import Ingredient

class ArtNatiFilter():
    error_label = "Natural/Artificial"
    key_string = "checked_boxes[art_nati][]"
    
    def __init__(self, querydict):
        checked_boxes = querydict.getlist(self.key_string)
        if checked_boxes == []:
            self.apply_filter = False
        else:
            self.apply_filter = True
            self.q_obj = self.get_query_object(checked_boxes)
            self.filtered_pks = Ingredient.objects.filter(self.q_obj).values_list('pk',flat=True)
        
    def get_query_object(self, checked_boxes):
        q_list = [Q(art_nati__iexact = art_nati_filter) for art_nati_filter in checked_boxes]
        return reduce(lambda x,y: x|y, q_list)
    
    def check_pk(self, pk):
        if pk not in self.filtered_pks: #the ingredient does not match the filter requirements
            return self.error_label

    
class AllergenExcludeFilter():
    error_label = "Allergens"
    key_string = "checked_boxes[allergen][]"
    
    def __init__(self, querydict):
        checked_boxes = querydict.getlist(self.key_string)
        if checked_boxes == []:
            self.apply_filter = False
        else:
            self.apply_filter = True
            allergen_filters = {}
            for cb in checked_boxes:
                allergen_filters[cb] = False 
            #finds the exclusion of any ingredients where the allergen_filter is True
            #including ingredients where all the allergen_filters are False
            self.filtered_pks = Ingredient.objects.filter(**allergen_filters).values_list('pk',flat=True)
        
    def check_pk(self, pk):
        if pk not in self.filtered_pks:
            return self.error_label


class MiscFilter():
    key_string = "checked_boxes[misc][]"
    
    def __init__(self,querydict):
        checked_boxes = querydict.getlist(self.key_string)
        
        if checked_boxes == []:
            self.apply_filter = False
        else:
            self.apply_filter = True
            self.filter_list = []
            for MyFilter in (Prop65Filter,GMOFilter,):
                myfilter = MyFilter(checked_boxes)
                if myfilter.apply_filter:
                    self.filter_list.append(MyFilter(checked_boxes))
            
            
    def check_pk(self, pk):
        return_messages = []
        for my_filter in self.filter_list:
            return_message = my_filter.check_pk(pk)
            if return_message is not None:
                return_messages.append(return_message)
        if return_messages != []:
            return return_messages

class SingleFilter():
    def check_pk(self, pk):
        if pk not in self.filtered_pks:
            return self.error_label


class Prop65Filter(SingleFilter):
    checked_box_name = "prop65"
    error_label = "Prop 65"
    
    def __init__(self, checked_boxes):
        
        if self.checked_box_name in checked_boxes:
            self.apply_filter = True
            self.filtered_pks = Ingredient.objects.exclude(prop65=True).values_list('pk',flat=True)
        else:
            self.apply_filter = False

class GMOFilter(SingleFilter):
    checked_box_name = "gmo"
    error_label = "GMO"
    
    def __init__(self, checked_boxes):
        if self.checked_box_name in checked_boxes:
            self.apply_filter = True
            self.filtered_pks = Ingredient.objects.exclude(gmo__icontains="yes").exclude(gmo__icontains="trace").values_list('pk',flat=True)
        else:
            self.apply_filter = False

# excludelist = diacetyl, nopg, gmo, prop65

    