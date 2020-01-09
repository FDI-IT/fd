# from django import template
#
# from access.models import Ingredient, FormulaException, FormulaCycleException
# from access.utils import explode_ingredient_gzl
#
# register = template.Library()
#
# @register.inclusion_tag('access/gzl_table.html')
# def ingredient_gzl_table(ingredient):
#     try:
#         explode_dict = explode_ingredient_gzl(ingredient, ingredient.gzl_traversal())
#         explode_dict['ingredient'] = ingredient
#     except FormulaCycleException as e:
#         raise
#     except FormulaException as e:
#         raise
#     except TypeError as e:
#         raise
#     explode_dict['number'] = ingredient.id
#     f = open('/tmp/django.dbg', 'w') #debug
#     print >>f, explode_dict #debug
#     f.close()
#     return explode_dict