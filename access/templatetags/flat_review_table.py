from decimal import Decimal, ROUND_HALF_UP

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.inclusion_tag('access/flavor/flat_review_table.html')
def flat_review_table(flavor):

    return {'flavor':flavor}
