from datetime import datetime

from django import forms

from formfieldset.forms import FieldsetMixin

class InvoiceReportFileForm(forms.Form):
    file = forms.FileField()
