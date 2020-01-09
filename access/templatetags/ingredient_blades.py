from decimal import Decimal

from django import template

register = template.Library()

@register.inclusion_tag('access/ingredient/ingredient_blades.html')
def ingredient_blades(ingredient):
    crit_list = []
    if ingredient.comments != '':
        crit_list.append(('Comments',ingredient.comments))
    if ingredient.cas != '':
        crit_list.append(('CAS',ingredient.cas))
    if ingredient.fema != '':
        crit_list.append(('FEMA',ingredient.fema))
    if ingredient.kosher != '':
        crit_list.append(('Kosher',ingredient.kosher))
        crit_list.append(('Last Kosher Date',ingredient.lastkoshdt))
    if ingredient.new_gmo != '':
        crit_list.append(('GMO',ingredient.new_gmo))
    if ingredient.natural_document_on_file:
        crit_list.append(('Natural Document On File',ingredient.natural_document_on_file))
    if ingredient.allergen != '':
        crit_list.append(('Allergen',ingredient.allergen))
    if ingredient.sprayed:
        crit_list.append(('Spray Dried',ingredient.sprayed))
    if ingredient.microsensitive != '':
        crit_list.append(('Microsensitive',ingredient.microsensitive))
    if ingredient.prop65:
        crit_list.append(('Prop 65',ingredient.prop65))
    if ingredient.nutri:
        crit_list.append(('Nutri',ingredient.nutri))
    if ingredient.transfat:
        crit_list.append(('Transfat',ingredient.transfat))
    return {
        'crit_list': crit_list,
            }
