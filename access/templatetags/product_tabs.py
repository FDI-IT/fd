from django import template

register = template.Library()

@register.inclusion_tag('access/product_tabs.html')
def product_tabs(product):
        return {
            'product_tabs': product.get_product_tabs(),
                }