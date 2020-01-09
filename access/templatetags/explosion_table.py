# from django import template
#
# from access.models import Flavor, FormulaException, FormulaCycleException
# from access.templatetags.review_table import explode
#
# register = template.Library()
#
# @register.inclusion_tag('access/flavor/explosion_table.html')
# def explosion_table(flavor):
#
#     try:
#         explode_dict = explode(flavor, flavor.formula_traversal())
#         explode_dict['flavor'] = flavor
#     except FormulaCycleException as e:
#         explode_dict['flavor'] = "RCE"
#         explode_dict = explode(flavor, flavor.ingredients.all())
#     except FormulaException as e:
#         explode_dict = {}
#         explode_dict['flavor'] = "RE"
#     except TypeError as e:
#         explode_dict = {}
#         explode_dict['flavor'] = "Type Error"
#     explode_dict['number'] = flavor.number
#     return explode_dict