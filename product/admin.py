from django.contrib import admin

from reversion.admin import VersionAdmin

#class ApplicationAdmin(VersionAdmin):
#    search_fields = ['flavor__number', 'flavor__name','application_type__name','memo']
#    raw_id_field = ["flavor"]
#admin.site.register(models.Application, ApplicationAdmin)
