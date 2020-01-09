from access.models import Formula, Ingredient

# not_sd_ingredients includes ingredients like apple flakes,
# sodium benzoate, rice tea
not_sd_ingredient_pins = (50, 5210, 750, 898, 1003)
not_sd_ingredints = Ingredient.objects.filter(id__in=not_sd_ingredient_pins)

arabic_ingredient_pins = (53, 54, 55, 56, 57, 58, 60, 3190, 3213, 3851, 4091)
arabic_ingredients = Ingredient.objects.filter(id__in=arabic_ingredient_pins)

for formula in Formula.objects.filter(ingredient__in=arabic_ingredients):
    flavor = formula.flavor
    if flavor.spraydried:
        continue
    not_sd_ingredient_count = flavor.ingredients.filter(id__in=not_sd_ingredient_pins).count()
    if not_sd_ingredient_count == 0:
        fname_lower = flavor.name.lower()
        ftype_lower = flavor.type.lower()
        if "emulsion" not in fname_lower and "emulsion" not in ftype_lower:
            print('"%s","%s"' % (flavor.number, flavor.name))

