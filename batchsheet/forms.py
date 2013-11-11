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
#     if Lot.objects.filter(number = num).count() > 0:
#         num = str(num)
#         raise ValidationError(mark_safe("<a href='/django/admin/newqc/lot/?q=%s'>A lot with this number already exists." % escape(num)))

        
class FlavorNumberField(forms.IntegerField):
    default_validators = [validate_flavor_number]
     
class LotNumberField(forms.CharField):
    default_validators = [validate_lot_number]

class NewLotForm(forms.Form):
    flavor_number = FlavorNumberField(label="", min_value=1)
    lot_number = LotNumberField(label="")
    amount = forms.DecimalField(max_digits=9, decimal_places=2) 
    
    def clean(self):
        cleaned_data = self.cleaned_data
        flavor_number = cleaned_data.get("flavor_number")
        lot_number = cleaned_data.get("lot_number")
        
        
        
        if flavor_number and lot_number: #only do this if both fields are valid so far
            
            try:
                lot = Lot.objects.get(number = lot_number)
            except:
                lot = None
                
            if lot != None:     
                lot_pk = lot.pk

                if lot.flavor.number == flavor_number:
                    raise ValidationError(mark_safe("This lot/flavor combination already exists. <a href='/django/batchsheet/update_lots/%s' style='color: #330066'>Update Lot</a>" % escape(str(lot_pk))))
                else:
                    raise ValidationError(mark_safe("There already exists a lot corresponding to a different flavor. <a href='/django/access/%s/#ui-tabs-6' style='color: #330066'>Find Lot</a> | <a href='/django/qc/lots/%s/' style='color: #330066'>Find Flavor </a>" % (escape(str(flavor_number)), escape(str(lot_pk)))))

        
        return cleaned_data

class UpdateLotForm(forms.Form):
    flavor_number = FlavorNumberField(label="", min_value=1)
    lot_number = LotNumberField(label="")
    amount = forms.DecimalField(max_digits=9, decimal_places=2) 
    
    def clean(self):
        cleaned_data = self.cleaned_data
        flavor_number = cleaned_data.get("flavor_number")
        lot_number = cleaned_data.get("lot_number")
        
        if flavor_number and lot_number: #only do this if both fields are valid so far
            
            try:
                lot = Lot.objects.get(number = lot_number)
                lot_pk = lot.pk
            except:
                raise ValidationError(mark_safe("<a href='/django/access/%s/#ui-tabs-6' style='color: #330066'>Invalid lot number." % escape(str(flavor_number))))
            
            if lot.flavor.number != flavor_number:
                raise ValidationError(mark_safe("There already exists a lot corresponding to a different flavor. <a href='/django/access/%s/#ui-tabs-6' style='color: #330066'>Find Lot</a> | <a href='/django/qc/lots/%s/' style='color: #330066'>Find Flavor </a>" % (escape(str(flavor_number)), escape(str(lot_pk)))))                      
    
            if lot.status != ('Created' | 'Batchsheet Printed'):
                raise ValidationError("This lot has status %s and cannot be updated." % lot.status)
            
        return cleaned_data            

'''
class AddLotRow(forms.Form):
    ingredient_number = FormulaIngredientField(label="")
    amount = forms.DecimalField(label="", max_digits=9, decimal_places=5)
    ingredient_pk = forms.IntegerField(required=False)
    '''