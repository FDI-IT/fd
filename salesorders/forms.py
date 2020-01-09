from django import forms
from django.forms import widgets

class SalesOrderReportFileForm(forms.Form):
    file = forms.FileField()

class SalesOrderSearch(forms.Form):
    search_string = forms.CharField(label="Search", required=False)
    
class SalesOrderFilterSelectForm(forms.Form):
    open = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            (True,"Open"),
            (False,"Closed"),
        ))
    
class ColorActivationForm(forms.Form):
    color = forms.BooleanField(required=False)