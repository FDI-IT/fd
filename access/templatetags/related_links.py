from decimal import Decimal, ROUND_HALF_UP

from django import template

register = template.Library()

@register.inclusion_tag('access/related_links.html')
def related_links(product):
        return {
            'related_links': product.get_related_links(),
                }