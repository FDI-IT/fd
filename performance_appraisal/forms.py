from datetime import datetime

from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.forms import widgets
from django.db import connection

from performance_appraisal.models import PerformanceAppraisal



class PerformanceAppraisalForm(forms.ModelForm):
    class Meta:
        model = PerformanceAppraisal
        exclude = () 
        
    def clean(self):
        super(PerformanceAppraisalForm, self).clean()
        cleaned_data = self.cleaned_data
        
        valid_scores = (1,2,3,4,5,6)
        
        if cleaned_data['period_start'] > cleaned_data['period_end']:
            raise forms.ValidationError("Start period can't come after end period.")
        return cleaned_data
        