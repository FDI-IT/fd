from access.models import *
from access.scratch import *
jj = Flavor.objects.get(number=9700)
boolean_field = jj._meta.fields[-1]
tt = type(boolean_field)
print tt
def trim():
    FormulaTree.objects.all().delete()
    LeafWeight.objects.all().delete()
    f_pks = set()
    i_pks = set()
    x = Flavor.objects.get(number=9700)
    build_tree(x)
    build_leaf_weights(x)
    
    for ft in FormulaTree.objects.all():
        nf = ft.node_flavor
        ni = ft.node_ingredient
        if nf is not None:
            f_pks.add(ft.node_flavor.pk)
        if ni is not None:
            i_pks.add(ft.node_ingredient.pk)
        
    for f in Flavor.objects.all():
        if f.pk in f_pks:
            print f
        else:
            f.formula_set.all().delete()
            f.delete()
            
    for i in Ingredient.objects.all():
        if i.pk in i_pks:
            print i
        else:
            i.delete()
    
    models = (
        FlavorIterOrder,
        ExperimentalLog,
        ShipTo,
        Shipper,
        Supplier,
        ExperimentalFormula,
        Customer,
        ExperimentalProduct,
        Incoming,
        PurchaseOrder,
        PurchaseOrderLineItem,
        LegacyPurchase,
    )
    for m in models:
        print "Deleting %s..." % m
        m.objects.all().delete()
        

    print i_pks
    print f_pks
    
def check_boolean_fields(obj):
    save_me = False
    for field in obj._meta.fields:
        if tt == type(field):
            x = getattr(obj, field.name)
            if x == None:
                setattr(obj, field.name, False)
                save_me = True
    if save_me:
        obj.save()
    