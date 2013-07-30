from django.contrib import admin
from reversion.admin import VersionAdmin
from invoices import models

class InvoiceAdmin(VersionAdmin):
    search_fields = ['number', 'customer',]
admin.site.register(models.Invoice, InvoiceAdmin)

class LineItemAdmin(VersionAdmin):
    search_fields = ['flavor']
admin.site.register(models.LineItem, LineItemAdmin)