from django import forms
from django.forms import widgets
from django.db import connection

from formfieldset.forms import FieldsetMixin

class SearchInput(widgets.Input): 
    input_type = 'search'

class MainSearch(forms.Form):
    search_space = forms.ChoiceField(
        choices=(
            ('flavor','Flavors'),
            ('ingredient','Raw Materials'),
            ('fema','FEMA'),
            ('experimental','Experimentals'),
            ('unified','F & E'),
            ('sales_order','Sales Orders'),
            ('purchase_order','Purchase Orders'),
            ('lot','Lots'),
            ('tsr','TSRs'),
        )
    )
    search_string = forms.CharField(label="Search", required=False, widget=SearchInput(attrs={'placeholder':'Search'}))
