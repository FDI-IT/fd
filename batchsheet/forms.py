from django import forms
from django.forms.formsets import BaseFormSet
from django.forms import widgets

from access.models import Flavor
from newqc.models import Lot

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from cgi import escape

class BatchSheetForm(forms.Form):
    flavor_number = forms.IntegerField(label="Flavor number", min_value=1, required=False)
    batch_amount = forms.DecimalField(label="Batch amount", 
                                      min_value=0, 
                                      max_digits=9, 
                                      decimal_places=3, required=False)
    lot_number=forms.IntegerField(label="Lot Number", required=False)


def validate_flavor_number(num):
    if Flavor.objects.filter(number = num).exists() == False:
        raise ValidationError(u"Please input a valid flavor number.")

def validate_lot_number(num):
#     if Lot.objects.filter(number = num).exists() == False:
#         raise ValidationError(mark_safe("<a href='/django/qc/lots/'>Please enter a valid lot number."))
    if num.isdigit() == False:
        raise ValidationError("Lot number must be an integer.")
    if Lot.objects.filter(number = num).count() > 0:
        num = str(num)
        raise ValidationError(mark_safe("<a href='/django/admin/newqc/lot/?q=%s'>A lot already exists with this number." % escape(num)))

        
class FlavorNumberField(forms.IntegerField):
    default_validators = [validate_flavor_number]
     
class LotNumberField(forms.CharField):
    default_validators = [validate_lot_number]

class NewLotForm(forms.Form):
    flavor_number = FlavorNumberField(label="", min_value=1)
    lot_number = LotNumberField(label="")
    amount = forms.DecimalField(max_digits=6, decimal_places=1) 
    