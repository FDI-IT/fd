from decimal import Decimal, ROUND_HALF_UP

from django import template

register = template.Library()

@register.inclusion_tag('access/experimental/flat_review_table.html')
def flat_review_table(experimental):

    return {'experimental':experimental}