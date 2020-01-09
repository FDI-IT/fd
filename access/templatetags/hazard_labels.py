from django import template

register = template.Library()

@register.inclusion_tag('hazards/label.html')
def small_flavor_hazard_label(flavor):
    
    return {'flavor':flavor}
    
    