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

def validate_flavor_number(num):
    if Flavor.objects.filter(number = num).exists() == False:
        raise ValidationError(u"Please input a valid flavor number.")

def validate_lot_number(num):
#     if Lot.objects.filter(number = num).exists() == False:
#         raise ValidationError(mark_safe("<a href='/qc/lots/'>Please enter a valid lot number."))
    if num.isdigit() == False:
        raise ValidationError("Lot number must be an integer.")
#     if Lot.objects.filter(number = num).count() > 0:
#         num = str(num)
#         raise ValidationError(mark_safe("<a href='/admin/newqc/lot/?q=%s'>A lot with this number already exists." % escape(num)))

        
class FlavorNumberField(forms.IntegerField):
    default_validators = [validate_flavor_number]
     
class LotNumberField(forms.CharField):
    default_validators = [validate_lot_number]

class NewLotForm(forms.Form):
    flavor_number = FlavorNumberField(label="", min_value=1)
    #lot_number = LotNumberField(label="")
    amount = forms.DecimalField(max_digits=9, decimal_places=2) 
    extra_weight = forms.DecimalField(max_digits=9, decimal_places=2, initial=0, required=False) 
    details = forms.CharField(widget=forms.HiddenInput,)
    '''
    def clean(self):
        cleaned_data = self.cleaned_data
        flavor_number = cleaned_data.get("flavor_number")
        lot_number = cleaned_data.get("lot_number")
        new_amount = cleaned_data.get("amount")
                
        
        if flavor_number and lot_number: #only do this if both fields are valid so far
            
            try:
                lot = Lot.objects.get(number = lot_number)
            except:
                lot = None
                
            if lot != None:     
                lot_pk = lot.pk

                if new_amount == lot.amount:
                    raise ValidationError(mark_safe("<a href='/access/%s/#ui-tabs-6' style='color: #330066'> This lot already exists with the same flavor and amount. </a>" % escape(str(flavor_number))))
                elif lot.flavor.number == flavor_number:
                    raise ValidationError(mark_safe("This lot/flavor combination already exists. <a href='/batchsheet/update_lots/%s/%s' style='color: #330066'>Update Lot</a>" % (escape(str(lot_pk)), escape(str(new_amount)))))
                else:
                    raise ValidationError(mark_safe("There already exists a lot corresponding to a different flavor. <a href='/access/%s/#ui-tabs-6' style='color: #330066'>Find Lot</a> | <a href='/qc/lots/%s/' style='color: #330066'>Find Flavor </a>" % (escape(str(flavor_number)), escape(str(lot_pk)))))

        
        return cleaned_data
    '''
    
class UpdateLotForm(forms.Form):
    flavor_number = FlavorNumberField(label="", min_value=1)
    lot_number = LotNumberField(label="")
    amount = forms.DecimalField(max_digits=9, decimal_places=2) 
    
    def clean(self):
        cleaned_data = self.cleaned_data
        flavor_number = cleaned_data.get("flavor_number")
        lot_number = cleaned_data.get("lot_number")
        new_amount = cleaned_data.get("amount")
        
        if flavor_number and lot_number: #only do this if both fields are valid so far
            
            try:
                lot = Lot.objects.get(number = lot_number)
                lot_pk = lot.pk
            except:
                raise ValidationError(mark_safe("<a href='/access/%s/#ui-tabs-6' style='color: #330066'>Invalid lot number." % escape(str(flavor_number))))
            
            if lot.flavor.number != flavor_number:
                raise ValidationError(mark_safe("There already exists a lot corresponding to a different flavor. <a href='/access/%s/#ui-tabs-6' style='color: #330066'>Find Lot</a> | <a href='/qc/lots/%s/' style='color: #330066'>Find Flavor </a>" % (escape(str(flavor_number)), escape(str(lot_pk)))))                      
            elif lot.status != ('Created' or 'Batchsheet Printed'):
                raise ValidationError("This lot has status %s and cannot be updated." % lot.status)
            elif new_amount == lot.amount:
                raise ValidationError(mark_safe("<a href='/access/%s/#ui-tabs-6' style='color: #330066'> This lot already exists with the same flavor and amount. </a>" % escape(str(flavor_number))))
                
            
        return cleaned_data            

def build_confirmation_rows(formset):
    confirmation_rows = []

    for form in formset.forms:
        info_row = {}
        if len(form._errors) == 0:
            cd = form.cleaned_data
            try:
                update_lot = Lot.objects.get(number = cd['lot_number'])
                #update_lot = Ingredient.get_formula_ingredient(form.cleaned_data['ingredient_number'])
            except KeyError:
                print "KEYERROR BUILDIN OLD INFO ROWS"
            
            info_row['lot_number'] = cd['lot_number']
            info_row['flavor_number'] = cd['flavor_number']
            info_row['old_amount'] = update_lot.amount
            info_row['old_status'] = update_lot.status
            info_row['new_amount'] = cd['amount']
            info_row['new_status'] = 'Created'
            
            '''
            #VALIDATION, should be located elsewhere?
            if info_row['new_amount'] == info_row['old_amount']:
                warning = 'The specified lot already has an amount of %s.' % old_amount
            else:
                warning = None
            
            info_row['warning'] = warning
            '''
            confirmation_rows.append(info_row)
                
        else:
            print "THERE ARE ERRORS IN THE FORM, BUILD_OLD_INFO_ROWS"
        

    return confirmation_rows

'''
class AddLotRow(forms.Form):
    ingredient_number = FormulaIngredientField(label="")
    amount = forms.DecimalField(label="", max_digits=9, decimal_places=5)
    ingredient_pk = forms.IntegerField(required=False)
    '''