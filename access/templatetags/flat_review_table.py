from decimal import Decimal, ROUND_HALF_UP

from django import template

register = template.Library()

@register.inclusion_tag('access/flavor/flat_review_table.html')
def flat_review_table(flavor):

    return {'flavor':flavor}