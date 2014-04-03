from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta

from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from access.models import ExperimentalLog

def make_double_tuple(list):
    for elem in list:
        yield (elem,elem)

class DateRangeForm(forms.Form):
    date_start = forms.DateField(initial=date(date.today().year,1,1))
    date_end = forms.DateField(initial=date.today())
    
class ExperimentalFilterSelectForm(forms.Form):
    initials_choices = ExperimentalLog.objects.order_by('initials').values_list('initials', flat=True).distinct()
    initials = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(make_double_tuple(initials_choices))
        )