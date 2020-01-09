from access.models import *
from django import template
from django.contrib.auth.models import Group, User


register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.filter(name='sensory_opt')
def check_sensory_opt_in(user):
    return Training.objects.filter(tester=user, test_type='sensory').exists()
