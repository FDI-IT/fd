from newqc.models import Retain, TestCard, ProductInfo, Lot, ImportRetain, RMImportRetain, RMInfo, RMRetain, ExperimentalRetain, RMTestCard, BatchSheet, ReceivingLog, LotWeightAdjustment, LotSOLIStamp, COA, TestResult
from django.contrib import admin
from reversion.admin import VersionAdmin

#admin.site.register(Retain)

class ReceivingLogAdmin(VersionAdmin):
    def queryset(self, request):
        qs = super(ReceivingLogAdmin, self).queryset(request)
        qs.extra(select={'receiving_year':'extract(year from date)','receiving_month':'extract(month from date)'})
        qs.order_by('-receving_year', '-receving_month', '-r_number')
        return qs
    
    search_fields = ['r_number','pin','description','supplier']
    list_display = ['r_number','date','pin','supplier','description','quantity_of_packages','package_size','units','lot','po_number','trucking_co','kosher_group']
    readonly_fields = ['r_number']
    list_editable = ['pin','supplier','description','quantity_of_packages','package_size','units','lot','po_number','trucking_co','kosher_group']
admin.site.register(ReceivingLog, ReceivingLogAdmin)

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

class BatchSheetAdmin(VersionAdmin):
    search_fields = ['lot__number']
admin.site.register(BatchSheet, BatchSheetAdmin)

class RMTestCardAdmin(VersionAdmin):
    search_fields = ['number']
admin.site.register(RMTestCard, RMTestCardAdmin)
    
#class TestCardAdmin(VersionAdmin):
#    search_fields = ['retain']
#admin.site.register(TestCard, TestCardAdmin)

class TestCardRetainFinderAdmin(VersionAdmin):
    search_fields = ['retain__retain']
admin.site.register(TestCard, TestCardRetainFinderAdmin)

class ProductInfoAdmin(VersionAdmin):
    search_fields = ['flavor__name','flavor__number','appearance','organoleptic_properties','testing_procedure','notes']
admin.site.register(ProductInfo, ProductInfoAdmin)
    
class LotAdmin(VersionAdmin):
    search_fields = ['number', 'flavor__number', 'flavor__name', 'date']
    raw_id_fields = ("flavor",)
    list_display = ("number", "sub_lot", "date", "flavor", "amount", "status",)
    list_display_links=("number", "flavor",)
    list_editable = ("status", "amount",)
admin.site.register(Lot, LotAdmin)

class LotWeightAdjustmentAdmin(VersionAdmin):
    search_fields = ['number', 'flavor__number']
    list_display = ['number','amount', 'flavor',]
    exclude = ('date','sub_lot','status','flavor',)
admin.site.register(LotWeightAdjustment, LotWeightAdjustmentAdmin)

class RMImportRetainAdmin(VersionAdmin):
    search_fields = ['number']
admin.site.register(RMImportRetain, RMImportRetainAdmin)

class RMInfoAdmin(VersionAdmin):
    search_fields = ['number']
admin.site.register(RMInfo, RMInfoAdmin)

class RMRetainAdmin(VersionAdmin):
    search_fields = ['r_number', 'lot', 'supplier',]
    raw_id_fields = ("ir",)
    list_display = ("r_number", "pin_review_link", "supplier", "lot", "status", "notes")
    list_display_links=("r_number",)
    list_editable = ("status", "notes")
    
    def pin_review_link(self, obj):
        return '<a href="/django/access/ingredient/pin_review/%s/">%s</a>' % (obj.pin, obj.pin)
    pin_review_link.allow_tags = True
admin.site.register(RMRetain, RMRetainAdmin)

class ExperimentalRetainAdmin(VersionAdmin):
    search_fields = ['retain', 'experimental_number']
admin.site.register(ExperimentalRetain, ExperimentalRetainAdmin)

class LotSOLIStampAdmin(VersionAdmin):
    search_fields = ['salesordernumber','lot__number',]
admin.site.register(LotSOLIStamp, LotSOLIStampAdmin)    

class COAAdmin(VersionAdmin):
    search_fields = ['lss__lot__number','lss_salesordernumber',]
admin.site.register(COA, COAAdmin)    

class TestResultAdmin(VersionAdmin):
    search_fields = ['coa_lss__lot__number','coa_lss_salesordernumber']
admin.site.register(TestResult, TestResultAdmin)    