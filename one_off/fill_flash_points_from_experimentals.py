from access.models import Flavor, ExperimentalLog

EMPTY_FIELD_LIST_WITH_EMPTY_STRING = (None,"",0)
EMPTY_FIELD_LIST = (None,0)
 
def fill_spec(flavor_spec_name, experimental_spec_name, compare_list):
    flavor_filter_kwargs = {
        '%s__in' % flavor_spec_name:compare_list,           
    }
    experimental_filter_kwargs = {
        'experimental_log__%s__in' % experimental_spec_name:compare_list
    }
    qs = Flavor.objects.filter(
                **flavor_filter_kwargs).exclude(
                experimental_log=None).exclude(
                **experimental_filter_kwargs)
    for f in qs:
        e = f.experimental_log.order_by(experimental_spec_name)[0]
        print(e)
        setattr(f, flavor_spec_name, getattr(e, experimental_spec_name))
        f.save()
        
def fill_flavor_specs_from_experimentals():
    
    fill_spec('flashpoint','flash', EMPTY_FIELD_LIST)
    fill_spec('spg','spg', EMPTY_FIELD_LIST)
    fill_spec('color','color', EMPTY_FIELD_LIST_WITH_EMPTY_STRING)
    fill_spec('organoleptics','organoleptics', EMPTY_FIELD_LIST_WITH_EMPTY_STRING)
    fill_spec('mixing_instructions','mixing_instructions', EMPTY_FIELD_LIST_WITH_EMPTY_STRING)
    fill_spec('yield_field','yield_field', EMPTY_FIELD_LIST)