from django.contrib import admin
from reversion.admin import VersionAdmin
from personnel import models

#class FormulaInline(admin.TabularInline):
#    model = Formula
#    extra = 0
#    
#class FlavorAdmin(admin.ModelAdmin):
#    inlines = [FormulaInline]

admin.site.register(models.UserProfile)
