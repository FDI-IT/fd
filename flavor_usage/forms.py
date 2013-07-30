from django import forms

from flavor_usage import models

class UsageForm(forms.ModelForm):
    class Meta:
        model = models.Application
        exclude = ['added_from_spreadsheet','original_spreadsheet_fields']
        widgets = {
            'flavor':forms.HiddenInput(),
        }