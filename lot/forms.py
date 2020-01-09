from django import forms
from django.forms.formsets import BaseFormSet
from django.forms import widgets

class BatchSheetForm(forms.Form):
    flavor_number = forms.IntegerField(label="Flavor number", min_value=1, required=False)
    batch_amount = forms.DecimalField(label="Batch amount", 
                                      min_value=0, 
                                      max_digits=9, 
                                      decimal_places=3, required=False)
    lot_number=forms.IntegerField(label="Lot Number", min_value=1200000, required=True)
