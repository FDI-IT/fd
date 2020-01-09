from django.contrib import admin
from reversion.admin import VersionAdmin
from unified_adapter import models

#class FormulaInline(admin.TabularInline):
#    model = Formula
#    extra = 0
#    
#class FlavorAdmin(admin.ModelAdmin):
#    inlines = [FormulaInline]

class ProductInfoAdmin(VersionAdmin):
    search_fields = ['name','keyword_1','keyword_2','description','memo','organoleptic_properties',]
    list_display = (
            'nat_art',
            'name',
            'experimental_number',
            'production_number',
            'same_as',
            'approved_promote',
            'sold',
            'location_code',
            'organic',
            'gmo_free',
            'kosher',
            'prop65',
            'no_msg',
            'no_pg',
            'no_diacetyl',
            'heat_stable',
            'duplication',
            'export_only',
            'liquid',
            'concentrate',
            'emulsion',
            'dry',
            'oil_soluble',
            'specific_gravity',
            'flash',
            'customer',
            'memo',
        )
    list_display_links=('name',)
    list_filter = ('sold',)
    #list_editable = ('sold','location_code')
admin.site.register(models.ProductInfo, ProductInfoAdmin)

class ApplicationAdmin(VersionAdmin):
    pass
admin.site.register(models.Application, ApplicationAdmin)