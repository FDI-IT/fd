from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms import widgets
from django.db import connection

from unified_adapter.models import ProductInfo

class BatchSheetForm(forms.Form):
    flavor_number = forms.IntegerField(label="Flavor number", min_value=1, required=False)
    batch_amount = forms.DecimalField(label="Batch amount", 
                                      min_value=0, 
                                      max_digits=9, 
                                      decimal_places=3, required=False)
    lot_number=forms.IntegerField(label="Lot Number", min_value=1200000, required=True)

def fetch_choices(sql_string, l_index=0, r_index=0):
    cursor = connection.cursor()
    cursor.execute(sql_string)
    choices = []
    for choice in cursor.fetchall():
        if choice[l_index] == '':
            choices.append(('blank','Blank'))
        else:
            choices.append((choice[l_index], choice[r_index]))
    return choices 

class ProductInfoFilterSelectForm(forms.Form):
#    allergens_choices = fetch_choices('select distinct "unified_adapter_productinfo"."allergens" from "unified_adapter_productinfo" ORDER BY "allergens" ASC')
    appl_choices = fetch_choices('select * from "unified_adapter_applicationtype" ORDER BY "unified_adapter_applicationtype"."name"', r_index=1)
#    approved_promote_choices = fetch_choices('select distinct "unified_adapter_productinfo"."approved_promote" from "unified_adapter_productinfo" ORDER BY approved_promote ASC')
#    initials_choices = fetch_choices('SELECT DISTINCT "unified_adapter_productinfo"."initials" FROM "unified_adapter_productinfo" ORDER BY initials ASC')
    kosher_choices = fetch_choices('select distinct "unified_adapter_productinfo"."kosher" from "unified_adapter_productinfo"')
    nat_art_choices = fetch_choices('select distinct "unified_adapter_productinfo"."nat_art" from "unified_adapter_productinfo" ORDER BY "nat_art" ASC')

#    approved_promote__in = forms.MultipleChoiceField(
#        label="Approved/Promote",
#        widget=widgets.CheckboxSelectMultiple,
#        required=False,
#        choices=approved_promote_choices
#        )
    nat_art__in = forms.MultipleChoiceField(
        label="Nat/Art",
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(nat_art_choices))
        )
#    allergens__in = forms.MultipleChoiceField(
#        label="Allergens",
#        widget=widgets.CheckboxSelectMultiple,
#        required=False,
#        choices=(tuple(allergens_choices))
#        )

    other = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            #('retains__notes', "Retains On File"),
            ('concentrate', "Concentrate"),
            ('dry', "Dry"),
            ('duplication','Duplication'),
            ('emulsion','Emulsion'),
            ('gmo_free','GMO Free'),
            ('heat_stable','Heat Stable'),
            ('liquid','Liquid'),
            ('no_diacetyl','No Diacetyl'),
            ('no_msg','No MSG'),
            ('no_pg','No PG'),
            ('oil_soluble','Oil Soluble'),
            ('organic','Organic'),
            ('prop65','Prop 65'),
            ('sold','Sold'),
            ('transfat','Transfat'),
            ('export_only','Export Only')
        ))

    application__application_type__id__in = forms.MultipleChoiceField(
        label="Application",
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(appl_choices))
        )
    
    kosher__in = forms.MultipleChoiceField(
        label="Kosher",
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(kosher_choices))
        )

#    initials__in = forms.MultipleChoiceField(
#        label="Initials",
#        widget=widgets.CheckboxSelectMultiple,
#        required=False,
#        choices=(tuple(initials_choices))
#        )