from django.contrib import admin
from reversion.admin import VersionAdmin
from solutionfixer import models

#class FormulaInline(admin.TabularInline):
#    model = Formula
#    extra = 0
#    
#class FlavorAdmin(admin.ModelAdmin):
#    inlines = [FormulaInline]

class SolutionAdmin(VersionAdmin):
    search_fields = ['ingredient__id']
admin.site.register(models.Solution, SolutionAdmin)
