from django.contrib import admin
from reversion.admin import VersionAdmin
from access import models
from django.db.models import Q, F

#class FormulaInline(admin.TabularInline):
#    model = Formula
#    extra = 0
#    
#class FlavorAdmin(admin.ModelAdmin):
#    inlines = [FormulaInline]

class MagentoAdmin(VersionAdmin):
    list_display = ('flavor', 'sku', 'description', 'price', 'short_description')
    list_editable = ('sku', 'description', 'price', 'short_description')
    search_fields = ['flavor__number']
    fields = ('flavor','sku','description','price','short_description')
    raw_id_fields = ('flavor',)
admin.site.register(models.MagentoFlavor, MagentoAdmin)

class FlavorAdmin(VersionAdmin):
    search_fields = ['number', 'name']
    fields = ('number','name','prefix','natart','label_type',
              'unitprice','productmemo','pricing_memo','rawmaterialcost','mixing_instructions','color',
              'organoleptics','flashpoint','spg','supportive_potential',
              'risk_assessment_group','risk_assessment_memo',
              'microtest',
              'discontinued','approved',
              'sulfites','sulfites_ppm','sulfites_usage_threshold',
              'no_pg','sold',
              'spraydried','lastprice','experimental',
              'lastspdate','valid',
              'kosher','kosher_id','solubility',
              'stability','nutri_on_file','flammability',
              'allergen','yield_field','pinnumber',
              'label_check','reactionextraction',
              'prop65','gmo','batfno',
              'organic','diacetyl',
              'indivisible','solvent',
              'ccp5','ccp6'
              )
admin.site.register(models.Flavor, FlavorAdmin)

class PurchaseOrderAdmin(VersionAdmin):
    search_fields = ['supplier__suppliername', 'supplier__suppliercode', 'number', 'purchaseorderlineitem__raw_material__product_name', 'purchaseorderlineitem__raw_material__rawmaterialcode', 'purchaseorderlineitem__raw_material__id']
admin.site.register(models.PurchaseOrder, PurchaseOrderAdmin)

class PurchaseOrderLineItemAdmin(VersionAdmin):
    search_fields = ['po__number', 'po__supplier__suppliername', 'raw_material__id', 'raw_material__rawmaterialcode', 'raw_material__id', 'raw_material__product_name']
    ordering = ['po__number']
admin.site.register(models.PurchaseOrderLineItem, PurchaseOrderLineItemAdmin)

class LegacyPurchaseAdmin(VersionAdmin):
    search_fields = ['suppliercode', 'rawmaterialcode', 'ponumber']
admin.site.register(models.LegacyPurchase, LegacyPurchaseAdmin)

class ShipperAdmin(VersionAdmin):
    search_fields = ['shipper_name']
admin.site.register(models.Shipper, ShipperAdmin)

class ShipToAdmin(VersionAdmin):
    search_fields = ['shiptoname']
admin.site.register(models.ShipTo, ShipToAdmin)

class SupplierAdmin(VersionAdmin):
    search_fields = ['suppliername', 'suppliercode']
    list_display = ['id','suppliername']
admin.site.register(models.Supplier, SupplierAdmin)

class AntisepticIngredientAdmin(VersionAdmin):
    search_fields = ['pin']
admin.site.register(models.AntisepticIngredient, AntisepticIngredientAdmin)

class ExperimentalFormulaAdmin(VersionAdmin):
    search_fields = ['experimental_num']
admin.site.register(models.ExperimentalFormula, ExperimentalFormulaAdmin)

class IngredientAdmin(VersionAdmin):
    search_fields = ['id', 'product_name']
    list_filter = ('inventoryng', 'has_allergen_text')
    list_display = ['id', 'art_nati', 'prefix', 'product_name', 'part_name2','flavornum','inventoryng', 'allergen','eggs','fish','milk','peanuts','soybeans','treenuts','wheat','sulfites','sunflower','sesame','mollusks','mustard','celery','lupines','yellow_5']
    list_editable = ['flavornum','inventoryng', 'allergen', 'eggs','fish','milk','peanuts','soybeans','treenuts','wheat','sulfites','sunflower','sesame','mollusks','mustard','celery','lupines','yellow_5']
    exclude = ('supplierid','committed','reorderlevel','old_lead_time','unitsonorder','sub_flavor')
admin.site.register(models.Ingredient, IngredientAdmin)

class ExperimentalLogAdmin(VersionAdmin):
    search_fields = ['experimentalnum','retain_number']
admin.site.register(models.ExperimentalLog, ExperimentalLogAdmin)

#class ProductSpecialInformationAdmin(VersionAdmin):
#    search_fields = ['flavor__number',]
#admin.site.register(models.ProductSpecialInformation, ProductSpecialInformationAdmin)

class DigitizedFormulaAdmin(VersionAdmin):
    search_fields=['experimental_log']
admin.site.register(models.DigitizedFormula,DigitizedFormulaAdmin)

class JIListAdmin(VersionAdmin):
    search_fields = ['a','b']
admin.site.register(models.JIList, JIListAdmin)

admin.site.register(models.Customer)

class IngredientDescriptionAdmin(VersionAdmin):
    list_display = ['id','product_name','comments','description']
    list_editable = ['comments','description']
    def queryset(self,request):
        return self.model.objects.exclude(Q(comments="") & Q(description=""))
admin.site.register(models.IngredientDescription, IngredientDescriptionAdmin)

class IngredientAllergenFixer(VersionAdmin):
    list_display = ['id','product_name','comments','allergen','crustacean',
        'eggs',
        'fish',
        'milk',
        'peanuts',
        'soybeans',
        'treenuts',
        'wheat',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',]
    list_editable = ['product_name','comments','allergen','crustacean',
        'eggs',
        'fish',
        'milk',
        'peanuts',
        'soybeans',
        'treenuts',
        'wheat',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',]
    exclude = ('supplierid','committed','reorderlevel','lead_time','unitsonorder','sub_flavor')
    def queryset(self,request):
        return self.model.objects.exclude(allergen__iexact="None").exclude(suppliercode__iexact="FDI").order_by('allergen')
admin.site.register(models.AllerIngredients, IngredientAllergenFixer)

class TSRAdmin(VersionAdmin):
    search_fields = ['number', 'customer__companyname', 'contact']
admin.site.register(models.TSR, TSRAdmin)

