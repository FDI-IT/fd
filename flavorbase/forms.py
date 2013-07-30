from django import forms
from django.forms.formsets import BaseFormSet
from django.forms import widgets

from access.models import Flavor
from newqc.models import Retain, TestCard, Lot

class AddRetainBatch(forms.Form):
    number_of_retains = forms.IntegerField(label="Number of retains", min_value=1)

class NewFlavorRetainForm(forms.Form):
    retain_number = forms.IntegerField(label="", min_value=1,
                                       widget=forms.HiddenInput)
    flavor_number = forms.IntegerField(label="", min_value=1)
    lot_number = forms.CharField(label="")
    weight = forms.IntegerField(label="", min_value=0)
    
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
        exclude = ('retain', 'large', 'preview', 'image_hash')
        
        
class RetainStatusForm(forms.ModelForm):
    
    class Meta:
        model = Retain
        fields = ('status', 'notes')