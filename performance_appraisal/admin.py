from django.contrib import admin

from reversion.admin import VersionAdmin

from performance_appraisal import models
from performance_appraisal import forms

class PerformanceAppraisalAdmin(VersionAdmin):
    form = forms.PerformanceAppraisalForm
    search_fields = ['employee_name', 'title']
admin.site.register(models.PerformanceAppraisal, PerformanceAppraisalAdmin)

class DepartmentAdmin(VersionAdmin):
    search_fields = ['name']
admin.site.register(models.Department, DepartmentAdmin)