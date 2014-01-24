from django import forms
from django.db import connection

from formfieldset.forms import FieldsetMixin

from access.models import Ingredient

# todo: consider creating a re-usable solvent list

INVENTORY_CHOICES = (
    ('','',),
    ('SL-8','SL-8'),
    ('SL-4','SL-4'),
    ('SLF-L','SLF-L'),
    ('SLF-O','SLF-O'),
    ('SD Lab','SD Lab'),
    ('Concentrates','Concentrates'),
    ('Refrigerator','Refrigerator'),
)

class FinishedProductLabelForm(forms.Form):
    production_number = forms.CharField()
    inventory_slot = forms.ChoiceField(choices=INVENTORY_CHOICES)
    
class RMLabelForm(forms.Form):
    pin = forms.CharField("PIN")


class ExperimentalForm(forms.Form):
    experimental_number = forms.CharField()
    inventory_slot = forms.ChoiceField(choices=INVENTORY_CHOICES)