from datetime import date
from django import forms
from django.forms.formsets import BaseFormSet
from django.forms import widgets
from django.db import connection

from access.models import Flavor
from newqc.models import Retain, RMRetain, TestCard, Lot, ReceivingLog, ProductInfo, STATUS_CHOICES, UNITS_CHOICES

class AddObjectsBatch(forms.Form):
    number_of_objects = forms.IntegerField(label="Number of objects", min_value=1)

class NewFlavorRetainForm(forms.Form):
    object_number = forms.IntegerField(label="", min_value=1,
                                       widget=forms.HiddenInput)
    flavor_number = forms.IntegerField(label="", min_value=1)
    lot_number = forms.CharField(label="")
    
    template_path = 'qc/add_retains.html'
    
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
    
class NewRMRetainForm(forms.Form):
    object_number = forms.IntegerField(label="R Number", min_value=1)
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
        return RMRetain(
                date=cd['date'],
                pin=cd['pin'],
                supplier=cd['supplier'],
                lot=cd['lot'],
                r_number=cd['object_number'],
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