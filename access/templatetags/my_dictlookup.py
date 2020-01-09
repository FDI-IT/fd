
from django import template
from django.conf import settings

register = template.Library()

def my_dictlookup(my_dict, key):
    """Gets an attribute of an object dynamically from a string name"""

    if key in my_dict:
        return my_dict[key]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID

register.filter('my_dictlookup', my_dictlookup)