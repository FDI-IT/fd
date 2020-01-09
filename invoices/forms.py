from datetime import datetime

from django import forms

class InvoiceReportFileForm(forms.Form):
    file = forms.FileField()
