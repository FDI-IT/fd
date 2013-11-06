from datetime import date
from django import forms
from django.forms.formsets import BaseFormSet
from django.forms import widgets
from django.db import connection
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from cgi import escape

from access.models import Flavor
import re

from access.models import Flavor
from newqc.models import Retain, RMRetain, TestCard, Lot, ReceivingLog, ProductInfo, STATUS_CHOICES, UNITS_CHOICES

class AddObjectsBatch(forms.Form):
    number_of_objects = forms.IntegerField(label="Number of objects", min_value=1)


def validate_flavor_number(num):
    if Flavor.objects.filter(number = num).exists() == False:
        raise ValidationError(u"Please input a valid flavor number.")
    
def validate_lot_number(num):
#     if Lot.objects.filter(number = num).exists() == False:
#         raise ValidationError(mark_safe("<a href='/django/qc/lots/'>Please enter a valid lot number."))
    if num.isdigit() == False:
        raise ValidationError("Lot number must be an integer.")
    if Lot.objects.filter(number = num).count() > 1:
        num = str(num)
        raise ValidationError(mark_safe("<a href='/django/admin/newqc/lot/?q=%s'>Multiple lots exist with this lot number." % escape(num)))

        
class FlavorNumberField(forms.IntegerField):
    default_validators = [validate_flavor_number]
     
class LotNumberField(forms.CharField):
    default_validators = [validate_lot_number]

class NewFlavorRetainForm(forms.Form):
       
    object_number = forms.IntegerField(label="", min_value=1,
                                       widget=forms.HiddenInput, )
    flavor_number = FlavorNumberField(label="", min_value=1)
    lot_number = LotNumberField(label="")
    
    template_path = 'qc/add_retains.html'
    
    def clean(self):
        cleaned_data = self.cleaned_data
        flavor_number = cleaned_data.get("flavor_number")
        lot_number = cleaned_data.get("lot_number")
        lot_pk = Lot.objects.get(number=lot_number).pk
        
        if flavor_number and lot_number: #only do this if both fields are valid so far
            raise_error = True
            lots = Lot.objects.filter(number = lot_number)
            if Lot.objects.filter(number = lot_number).exists() == True:
                for lot in lots:
                    if lot.flavor.number == flavor_number:
                        raise_error = False
                if raise_error == True:
                    raise ValidationError(mark_safe("The given lot number does not correspond to the given flavor number. <a href='/django/access/%s/#ui-tabs-5' style='color: #330066'>Find Lot</a> | <a href='/django/qc/lots/%s/' style='color: #330066'>Find Flavor </a>" % (escape(str(flavor_number)), escape(str(lot_pk)))))
            else:
                raise ValidationError(mark_safe("<a href='/django/access/%s/#ui-tabs-5' style='color: #330066'>Invalid lot number." % escape(str(flavor_number))))
        
        return cleaned_data

            
    
    @staticmethod
    def prepare_formset_kwargs(number_of_objects):
        next_object_number = Retain.get_next_object_number()
        for new_object_number in range(next_object_number, next_object_number+number_of_objects):
            yield {'object_number':new_object_number}

                
    def create_from_cleaned_data(self):
        cd = self.cleaned_data
        lot_number = cd['lot_number']
        f = Flavor.objects.get(number=cd['flavor_number'])
        l = Lot.objects.get(number=lot_number, flavor=f)
        return Retain(
                retain=cd['object_number'],
                lot=l,
                date=cd['date'],
                status="Pending",
            )
    
class NewReceivingLogForm(forms.Form):
    r_number = forms.IntegerField(label="", min_value=1, widget=forms.HiddenInput)
    pin = forms.IntegerField(label="", min_value=1)
    supplier = forms.CharField(label="", max_length=40)
    description = forms.CharField(label="", max_length=120)
    quantity_of_packages = forms.DecimalField(label="",max_digits=4, decimal_places=1)
    package_size = forms.DecimalField(label="",max_digits=6, decimal_places=3)
    units = forms.ChoiceField(label="",choices=UNITS_CHOICES)
    lot = forms.CharField(label="",max_length=40)
    po_number = forms.IntegerField(label="",min_value=1)
    trucking_co = forms.CharField(label="",max_length=40)
    kosher_group = forms.CharField(label="",max_length=40)
    template_path = 'qc/add_receiving_log.html'
        
    @staticmethod
    def prepare_formset_kwargs(number_of_objects):
        next_r_number = ReceivingLog.get_next_r_number()
        for new_r_number in range(next_r_number, next_r_number+number_of_objects):
            yield {'r_number':new_r_number}
            
    
                    
    def create_from_cleaned_data(self):
        return ReceivingLog(**self.cleaned_data)


def validate_rnumber(rnum):
    checkRNum = re.compile(r"^[Rr]?[-\s]?[0-9]+$")
    
    m = checkRNum.match(rnum)
    
    if m is None:
        raise ValidationError(u"Please input a valid R Number.")
        
        

class RNumberField(forms.CharField):
    default_error_messages = {
        'invalid': (u'Enter a valid R Number.'),
    }
    default_validators = [validate_rnumber]
    
class NewRMRetainForm(forms.Form):
    object_number = RNumberField(label="R Number")
    pin = forms.IntegerField(min_value=1)
    lot = forms.CharField()
    supplier = forms.CharField()
    
    template_path = 'qc/add_rm_retains.html'
    
    @staticmethod
    def prepare_formset_kwargs(number_of_objects):
        for x in range(0,number_of_objects):
            yield {}
        
            
    def create_from_cleaned_data(self):    
        cd = self.cleaned_data
        
        num = re.compile(r"[0-9]+$")
        temp = num.search(cd['object_number'])
  
        return RMRetain(
                date=cd['date'],
                pin=cd['pin'],
                supplier=cd['supplier'],
                lot=cd['lot'],
                r_number=temp.group(),
                status="Pending"            
            )
    

class ResolveRetainForm(forms.ModelForm):
    class Meta:
        model = Retain
        exclude = ('retain', 'lot', 'sub_lot', 'amount', 'content_type', 'object_id', 'product')

class ResolveLotForm(forms.ModelForm):
    class Meta:
        model = Lot
        exclude = ('date', 'number', 'sub_lot', 'amount', 'flavor')
    
class ResolveTestCardForm(forms.ModelForm):
    class Meta:
        model = TestCard
        exclude = ('large', 'preview', 'image_hash', 'thumbnail')
        widgets = {
            'notes':forms.TextInput,
            'retain':forms.HiddenInput,
            'status':forms.Select,
        }

class ProductInfoForm(forms.ModelForm):
    class Meta:
        model = ProductInfo
        exclude = ('flavor','retain_on_file','original_card','flash_point','specific_gravity',)
        widgets = {
            'testing_procedure':forms.TextInput,
            'notes':forms.TextInput,
        }
        
class RetainStatusForm(forms.ModelForm):
    
    class Meta:
        model = Retain
        fields = ('status', 'notes')
        
class LotFilterSelectForm(forms.Form):
    cursor = connection.cursor()
    cursor.execute('select distinct newqc_lot.status from newqc_lot')
    status_choices = list(STATUS_CHOICES)
    for choice in cursor.fetchall():
        new_choice = (choice[0],choice[0])
        if new_choice not in STATUS_CHOICES:
            status_choices.append(new_choice)
    status = forms.MultipleChoiceField(
            widget = widgets.CheckboxSelectMultiple,
            required=False,
            choices=status_choices
        )