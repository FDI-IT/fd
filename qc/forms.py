from django import forms
from django.forms.formsets import BaseFormSet
from fd.flavorbase.models import Flavor
from fd.qc.models import Retain
from fd.qc.widgets import RetainStatusChangeWidget
from django.forms.widgets import RadioSelect,CheckboxSelectMultiple

class NewFlavorRetainForm(forms.Form):
    """
    Add a new Flavor Retain.
    """
    flavor_choice = forms.ModelChoiceField(queryset=Flavor.objects.all()) 
    amount = forms.DecimalField(min_value=0,
                                widget=forms.TextInput(attrs={'size':'6'}))
    lot = forms.IntegerField(min_value=0,
                             widget=forms.TextInput(attrs={'size':'7'}))
    sub_lot = forms.IntegerField(min_value=0, required=False,
                             widget=forms.TextInput(attrs={'size':'6'}))
class NewRawMaterialRetainForm(forms.Form):
    """
    Add a new Raw Material Retain. Needs tweaking: convert suplier to a 
    drop-down menu, etc.
    """
    number = forms.IntegerField(min_value=0)
    supplier = forms.CharField(max_length=25)
    supplier_lot = forms.CharField(max_length=25)
    rec_number = forms.IntegerField(min_value=0)

class RetainStatusChangeForm(forms.ModelForm):
    """
    A form to select a status for a retain.
    """
    status = forms.ChoiceField(widget=RetainStatusChangeWidget,
                                   choices=([
                                       ['Passed',''],
                                       ['Rejected',''],
                                       ['Resample',''],
                                       ['Hold',''],
                                       ['Pending','']
                                   ]),
                                   initial='Passed'
                                  )
    class Meta:
        model = Retain
        fields = ['status']

class BaseFlavorFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        lots = []
        for form in self.forms:
            try:
                lot = form.cleaned_data['lot']
                [str(form.cleaned_data['lot']), 
                            str(form.cleaned_data['sub_lot'])]
                lot = ''.join([str(form.cleaned_data['lot']),
                               str(form.cleaned_data['sub_lot'])])
                if lot in lots:
                    raise forms.ValidationError, \
                            "New retains must have distinct lots."
                lots.append(lot)
            except KeyError:
                pass

class RetainFilterSelectForm(forms.Form):
    status = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        required=False,
        choices=[
            ["Passed","Passed"],
            ["Rejected","Rejected"],
            ["Resample","Resample"],
            ["Hold","Hold"],
            ["Pending","Pending"],
        ])
