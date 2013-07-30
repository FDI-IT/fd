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

class SolutionForm(forms.Form):
    ingredient_picker = forms.CharField()
    pin = forms.CharField()
    nat_art = forms.CharField()
    pf = forms.CharField()
    product_name = forms.CharField()
    product_name_two = forms.CharField()
    concentration = forms.ChoiceField(
                        choices=(
                                 ('',''),
                                 ('0.01%','0.01%'),
                                 ('0.05%','0.05%'),
                                 ('0.1%','0.1%'),
                                 ('0.2%','0.2%'),
                                 ('0.5%','0.5%'),
                                 ('1%','1%'),
                                 ('2%','2%'),
                                 ('5%','5%'),
                                 ('10%','10%'),
                                 ('25%','25%'),
                                 ))
    solvent = forms.ChoiceField(
                    choices=(
                             ('',''),
                             ('PG','Propylene Glycol'),
                             ('EtOH','Ethyl Alcohol'),
                             ('Triacetin','Triacetin'),
                             ('Neobee','Neobee'),
                             ('Water','Water'),
                             ('Soybean Oil','Soybean Oil'),
                             ('N/A - Powder','N/A - Powder'),
                             ),)

class ExperimentalForm(forms.Form):
    experimental_number = forms.CharField()
    inventory_slot = forms.ChoiceField(choices=INVENTORY_CHOICES)