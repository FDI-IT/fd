from django import template
from django.forms.widgets import Select

#from haystack.forms import ModelSearchForm

from mysearch.forms import MainSearch 
register = template.Library()

def mainsearch(context):
#    my_form = ModelSearchForm()
#    choices = my_form.fields['models']
#    my_form.fields['models'].widget = Select(choices=my_form.fields['models'].choices)
    my_form = context.get('ms', None)
    if my_form:
        return {
                'mainsearch': my_form,
                    }    
    else:
        try:
            search_request_GET = context['request'].session.get('search_request_GET', None)
        except:
            search_request_GET = None
        if search_request_GET:
            return {
                    'mainsearch': MainSearch(search_request_GET)
                    }
        else:
            return {
                    'mainsearch': MainSearch()
                    }
register.inclusion_tag('mysearch/mainsearch.html', takes_context=True)(mainsearch)

def rm_search(context):
    return mainsearch(context)
register.inclusion_tag('mysearch/rm_search.html', takes_context=True)(rm_search)

def new_pin_flavor_search(context):
    return mainsearch(context)
register.inclusion_tag('mysearch/new_pin_flavor_search.html', takes_context=True)(new_pin_flavor_search)
