import datetime
from decimal import Decimal, ROUND_HALF_UP

from django import template
from django.db.models import Q

from newqc.models import Retain

register = template.Library()

@register.inclusion_tag('qc/dashboard.html')
def dashboard():
    retains = Retain.objects.filter(date=datetime.date.today())
    not_passed = retains.filter(~Q(status__exact='Passed'))
    pending = retains.filter(status__exact='Pending')
    return {
       'retains': retains,
       'not_passed': not_passed,
       'pending': pending,
       }