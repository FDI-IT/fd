from django.contrib import admin
from reversion.admin import VersionAdmin
from lot import models

#class FormulaInline(admin.TabularInline):
#    model = Formula
#    extra = 0
#    
#class FlavorAdmin(admin.ModelAdmin):
#    inlines = [FormulaInline]

class LotAdmin(VersionAdmin):
    search_fields = ['number', 'flavor__number', 'flavor__name']
    raw_id_fields = ("flavor",)
    list_display = ("number", "date", "sub_lot", "status", "amount", "flavor")
    list_display_links=("number", "flavor",)
    list_editable = ("status", "amount",)
admin.site.register(models.Lot, LotAdmin)