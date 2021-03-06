from django.contrib import admin
from reversion.admin import VersionAdmin
from access import models
from django.db.models import Q, F

from hazards.models import GHSIngredient, IngredientCategoryInfo

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
    fields = ('number','name','prefix','natart','label_type','phase','product_category',
              'unitprice','productmemo','pricing_memo','mixing_instructions','color',
              'organoleptics','flashpoint','spg','supportive_potential',
              'risk_assessment_group','risk_assessment_memo',
              'microtest',
              'discontinued','approved',
              #'sulfites','sulfites_ppm','sulfites_usage_threshold',
              #'no_pg','sold',
              'spraydried',#'lastprice','experimental',
              #'lastspdate','valid',
              'kosher','kosher_id','solubility',
              'stability','flammability',
              'yield_field','pinnumber',
              'label_check','reactionextraction',
              'prop65','vegan','ovo_vegan','batfno',
              'diacetyl',
              #'indivisible','solvent',
              'ccp5','ccp6','keep_refrigerated',
              #'nutri_on_file','allergen', 'rawmaterialcost'
              )
admin.site.register(models.Flavor, FlavorAdmin)

class PurchaseOrderAdmin(VersionAdmin):
    search_fields = ['supplier__name', 'supplier__suppliercode', 'number', 'purchaseorderlineitem__raw_material__product_name', 'purchaseorderlineitem__raw_material__rawmaterialcode', 'purchaseorderlineitem__raw_material__id']
admin.site.register(models.PurchaseOrder, PurchaseOrderAdmin)

class PurchaseOrderLineItemAdmin(VersionAdmin):
    search_fields = ['po__number', 'po__supplier__name', 'raw_material__id', 'raw_material__rawmaterialcode', 'raw_material__id', 'raw_material__product_name']
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

 #change this to reflect new allergens
class IngredientAdmin(VersionAdmin):
    search_fields = ['id', 'product_name']
    list_filter = ('inventoryng', 'has_allergen_text')
    list_display = ['id','art_nati','prefix','product_name','part_name2','flavornum','inventoryng',
                    #'allergen',
                    'crustacean',
                    'eggs',
                    'fish',
                    'milk',
                    'peanuts',
                    'soybeans',
                    'treenuts',
                    'wheat',
                    'sulfites',
                    'sunflower',
                    'sesame',
                    'mollusks',
                    'mustard',
                    'celery',
                    'lupines',
                    'yellow_5',
                    'barley_gluten'
                    ]
    list_editable = ['flavornum','inventoryng',
                     #'allergen',
                     'crustacean',
                     'eggs',
                     'fish',
                     'milk',
                     'peanuts',
                     'soybeans',
                     'treenuts',
                     'wheat',
                     'sulfites',
                     'sunflower',
                     'sesame',
                     'mollusks',
                     'mustard',
                     'celery',
                     'lupines',
                     'yellow_5',
                     'barley_gluten'
                     ]
    exclude = ('supplierid','committed','reorderlevel','old_lead_time','unitsonorder','sub_flavor','allergen','has_allergen_text')
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

class IngredientDescriptionAdmin(admin.ModelAdmin):
    list_display = ['id','product_name','comments','description']
    list_editable = ['comments','description']
    def get_queryset(self,request):
        return self.model.objects.exclude(Q(comments="") & Q(description=""))
admin.site.register(models.IngredientDescription, IngredientDescriptionAdmin)

class IngredientAllergenFixer(admin.ModelAdmin):
    list_display = ['id','product_name','comments',#'allergen',
        'crustacean',
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
    list_editable = ['product_name','comments',#'allergen',
        'crustacean',
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
    def get_queryset(self,request):
        return self.model.objects.exclude(allergen__iexact="None").exclude(suppliercode__iexact="FDI").order_by('allergen')
admin.site.register(models.AllerIngredients, IngredientAllergenFixer)

class PendingFlavorRiskAssessment(admin.ModelAdmin):
    list_display = ['number','name','risk_assessment_group','risk_assessment_memo']
    list_editable = ['risk_assessment_group','risk_assessment_memo']
    radio_fields = {'risk_assessment_group':admin.VERTICAL}
    #exclude = ()
    def get_queryset(self,request):
        return self.model.objects.filter(valid=True).filter(approved=True).filter(risk_assessment_group=7).order_by('number')
admin.site.register(models.FlavorRiskAssessment, PendingFlavorRiskAssessment)

class TSRAdmin(VersionAdmin):
    search_fields = ['number', 'customer__companyname', 'contact']
admin.site.register(models.TSR, TSRAdmin)

class IncomingAdmin(VersionAdmin):
    search_fields = ['incomingid', 'incname', 'inccompany']
admin.site.register(models.Incoming, IncomingAdmin)


class ProductCatgeory(VersionAdmin):
    search_fields = ['name']
admin.site.register(models.ProductCategory, ProductCatgeory)

class SolventAdmin(VersionAdmin):
    search_fields = ['ingredient__id']
admin.site.register(models.Solvent, SolventAdmin)

class FlavorSpecificationAdmin(VersionAdmin):
    search_fields = ['flavor__name', 'name']
    fields = ('name','specification','flavor'
              )
    raw_id_fields = ('flavor',)
admin.site.register(models.FlavorSpecification, FlavorSpecificationAdmin)

class ReconciledFlavorAdmin(VersionAdmin):
    search_fields = ['flavor__name', 'flavor__number']
admin.site.register(models.ReconciledFlavor, ReconciledFlavorAdmin)

class IngredientCategoryRelationshipInline(admin.TabularInline):
    model = IngredientCategoryInfo
    extra = 1

class GHSIngredientAdmin(VersionAdmin):
    search_fields = ['cas', 'name']
    inlines = (IngredientCategoryRelationshipInline,)
admin.site.register(GHSIngredient, GHSIngredientAdmin)

class LocationCodeAdmin(VersionAdmin):
    search_fields = ['location_code', 'content_object__number']
admin.site.register(models.LocationCode, LocationCodeAdmin)
