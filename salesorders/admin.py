from django.contrib import admin
from reversion.admin import VersionAdmin
from salesorders import models

class SalesOrderNumberAdmin(VersionAdmin):
    search_fields = ['number', 'customer',]
admin.site.register(models.SalesOrderNumber, SalesOrderNumberAdmin)

class LineItemAdmin(VersionAdmin):
    search_fields = ['flavor']
admin.site.register(models.LineItem, LineItemAdmin)