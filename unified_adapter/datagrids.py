from djblets.datagrid.grids import Column, DataGrid
from unified_adapter import models

#class FormulaInline(admin.TabularInline):
#    model = Formula
#    extra = 0
#    
#class FlavorAdmin(admin.ModelAdmin):
#    inlines = [FormulaInline]
class ProductInfoDataGrid(DataGrid):
    allergens = Column('Allergens', sortable=True,)
    approved_promote = Column('Approved', sortable=True,)
    concentrate = Column('Conc', sortable=True,)
    customer = Column('Customer', sortable=True,)    
    description = Column('Desc', sortable=True,)
    dry = Column('Dry', sortable=True,)
    duplication = Column('Dup', sortable=True,)
    emulsion = Column('Emul', sortable=True,)
    experimental_number = Column('ExNumber', sortable=True,)
    export_only = Column('Export', sortable=True,)
    flash = Column('Flash', sortable=True,)
    gmo_free = Column('GMO Free', sortable=True,)
    heat_stable = Column('Heat Stable', sortable=True,)
    initials = Column('Initials', sortable=True,)
    keyword_1 = Column('KW1', sortable=True,)
    keyword_2 = Column('KW2', sortable=True,)
    kosher = Column('Kosher', sortable=True,)
    liquid = Column('Liquid', sortable=True,)
    location_code = Column('Location Code', sortable=True,)
    memo = Column('Memo', sortable=True,)
    microsensitive = Column('Microsensitive', sortable=True,)
    name = Column('Name', sortable=True,)
    nat_art = Column('Nat/Art', sortable=True,)
    no_diacetyl = Column('No Diacetyl', sortable=True,)
    no_msg = Column('No MSG', sortable=True,)
    no_pg = Column('No PG', sortable=True,)
    nutri_on_file = Column('Nutri On File', sortable=True,)
    organic = Column('Organic', sortable=True,)
    organoleptic_properties = Column('Organoleptic Properties', sortable=True,)
    oil_soluble = Column('Oil Soluble', sortable=True,)
    percentage_yield = Column('Yield', sortable=True,)
    production_number = Column('ProNumber', sortable=True,)
    prop65 = Column('Prop 65', sortable=True,)
    same_as = Column('Same As', sortable=True,)
    sold = Column('Sold', sortable=True,)
    solubility = Column('Solubility', sortable=True,)
    specific_gravity = Column('Specific Gravity', sortable=True,)
    testing_procedure = Column('Testing Procedure', sortable=True,)
    transfat = Column('Transfat', sortable=True,)
    unitprice = Column('Unit Price', sortable=True,)
    
    def __init__(self, request):
        DataGrid.__init__(self,request,queryset=models.ProductInfo.objects.all(),title="Product Info")
        self.default_sort = ['name']
        self.default_columns = ['name','production_number']
        self.profile_sort_field = "sort_user_columns"
        self.profile_columns_field = "user_columns"
