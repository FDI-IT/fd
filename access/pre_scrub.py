from django.db import transaction

from access.models import Flavor, Ingredient, FlavorIterOrder, FormulaException

# time 0.
class YieldFieldValidator():
    @transaction.atomic
    def validate(self):
        for f in Flavor.objects.exclude(yield_field=100):
            if f.yield_field is None or f.yield_field == 0:
                f.yield_field = 100
                f.save()

# time 22 s
class ComplexIngredientValidator():
    """
    Checks that all ingredients with a flavornum point to a valid flavor.
    """
    @transaction.atomic
    def validate(self):
        complex_ingredients = Ingredient.objects.exclude(flavornum=None).exclude(flavornum=0)
        flavor_nums = complex_ingredients.values_list('flavornum',flat=True)
        flavors = Flavor.objects.filter(number__in=flavor_nums)
        for ing in complex_ingredients: 
            try:
                f = flavors.get(number=ing.flavornum)
                autoname = f.__str__()[:60]
                if ing.product_name != autoname:
                    ing.comments = "%s -- Changed name from '%s'" % (ing.comments, ing.product_name)
                    ing.product_name = autoname
                    ing.sub_flavor=f
                    ing.save()
            except Flavor.DoesNotExist:
                ing.comments = "%s -- Flavornum could not be connected: %s" % (ing.comments, ing.flavornum)
                ing.flavornum = 0
                ing.save()
                print("FAILED TO GET FLAVOR #%s" % ing.flavornum)

                
                