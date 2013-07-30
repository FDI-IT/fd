from newqc.models import Retain, TestCard, ProductInfo, Lot, ImportRetain
from django.contrib import admin
from reversion.admin import VersionAdmin

#admin.site.register(Retain)

class RetainAdmin(VersionAdmin):
    search_fields = ['retain', 'lot__number', 'lot__flavor__number', 'lot__flavor__name']
    raw_id_fields = ("lot","ir")
    list_display = ("retain", "flavor_link", "lot", "status", "notes")
    list_display_links=("retain",)
    list_editable = ("status", "notes")
    
    def flavor_link(self, obj):
        return '<a href="%s">%s-%s</a>' % (obj.lot.flavor.get_absolute_url(), obj.lot.flavor.prefix, obj.lot.flavor.number)
    flavor_link.allow_tags = True
admin.site.register(Retain, RetainAdmin)

class ImportRetainAdmin(VersionAdmin):
    search_fields = ['number']
admin.site.register(ImportRetain, ImportRetainAdmin)
    
class TestCardAdmin(VersionAdmin):
    search_fields = ['retain']
admin.site.register(TestCard, TestCardAdmin)

class ProductInfoAdmin(VersionAdmin):
    search_fields = ['content_object']
admin.site.register(ProductInfo, ProductInfoAdmin)
    
class LotAdmin(VersionAdmin):
    search_fields = ['number', 'flavor__number', 'flavor__name', 'date']
    raw_id_fields = ("flavor",)
    list_display = ("number", "sub_lot", "date", "flavor", "amount", "status",)
    list_display_links=("number", "flavor",)
    list_editable = ("status", "amount",)
admin.site.register(Lot, LotAdmin)
    