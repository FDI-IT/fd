from docvault.models import Page, Doc
from django.contrib import admin
from reversion.admin import VersionAdmin

class DocAdmin(VersionAdmin):
    pass
admin.site.register(Doc, DocAdmin)

class PageAdmin(VersionAdmin):
    pass
admin.site.register(Page, PageAdmin)

#class LotAdmin(VersionAdmin):
#    search_fields = ['number', 'flavor__number', 'flavor__name', 'date']
#    raw_id_fields = ("flavor",)
#    list_display = ("number", "sub_lot", "date", "flavor", "amount", "status",)
#    list_display_links=("number", "flavor",)
#    list_editable = ("status", "amount",)
#admin.site.register(Lot, LotAdmin)
#    