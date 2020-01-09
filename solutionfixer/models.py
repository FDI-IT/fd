from decimal import Decimal

from django.db import models, transaction
from access.models import Ingredient, Flavor, Formula

# Create your models here.
class Solution(models.Model):
    ingredient = models.OneToOneField(Ingredient, related_name='ing_obj', db_index=True,on_delete=models.CASCADE)
    my_base = models.ForeignKey(Ingredient, null=True, blank=True, related_name='my_base', db_index=True,on_delete=models.CASCADE)
    my_solvent = models.ForeignKey(Ingredient, null=True, blank=True, related_name='my_solvent', db_index=True,on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    status = models.ForeignKey('SolutionStatus', blank=True, null=True,on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s %s %s" % (self.ingredient.id,
                                   self.ingredient.art_nati,
                                   self.ingredient.prefix,
                                   self.ingredient.product_name)

    class Meta:

        ordering = ['ingredient']

    def calculate_price(self):
        if self.my_base!=None and self.my_solvent!=None:
            concentration_decimal = Decimal(self.percentage)/100
            component_price = self.my_base.unitprice * concentration_decimal
            solvent_price = self.my_solvent.unitprice * (1-concentration_decimal)
            unit_price = (component_price + solvent_price).quantize(Decimal('0.000')) #make it 3 decimal places

            return unit_price

        else:
            return False #will return false if the solution is missing a base and/or a solvent

    def update_ingredient_price(self):
        unit_price = self.calculate_price()
        if unit_price:
            self.ingredient.update_price(unit_price)
            return True
        else:
            return False #will return false if the solution is missing a base and/or a solvent

    def update_fields(self):
        #TODO: this function will update certain fields based on the base and solvent
        #prop65, O.C., GMO, Kosher, Micro, Allergen

        pass

class SolutionStatus(models.Model):
    status_name = models.CharField(max_length=20)
    status_order = models.PositiveSmallIntegerField()

    def __str__(self):
        return "%s" % (self.status_name)

    class Meta:
        ordering = ['status_order']

class SolutionMatchCache(models.Model):
    my_pk = models.AutoField(primary_key=True)
    id = models.IntegerField()
    value = models.IntegerField()
    label = models.CharField(max_length=150)
    solution = models.ForeignKey('Solution',on_delete=models.CASCADE)


class ProcessSolutions:

    def __init__(self):
        self.solutions = Solution.objects.filter(status__id=3)

    def process(self):
        for solution in self.solutions:
            ing = solution.ingredient
            base_price = solution.my_base.unitprice
            solvent_price = solution.my_solvent.unitprice
            base_price_component = base_price * solution.percentage / 100
            solvent_price_component = solvent_price * (100-solution.percentage) / 100
            ing.unitprice = base_price_component + solvent_price_component
            ing.save()

@transaction.atomic
def convert_solution_into_formula(solution):
    from access.scratch import recalculate_guts #have to import here, importing above causes circualar import
    '''
    This script will convert an old solution into a formula
    The goal is to remove all 'solutions' entirely

    Steps:
    1. Make sure the solution has both a solvent and a base, and that the solvent is in the solvent list
    2. Create a new permanent number which will contain the formula of the solution
    3. Create the formula using the base and solvent
    4. Set the old solution's ingredient sub_flavor to the newly created flavor-solution
    '''

    ingredient = solution.ingredient
    base = solution.my_base
    solvent = solution.my_solvent

    if base != None and solvent != None and solvent in Ingredient.objects.exclude(solvent_listing=None):

        #create the new flavor and its formula using the base and solvent of the solution
        new_flavor = Flavor(
            number = Flavor.get_next_solution_number(),
            name = solution.ingredient.product_name,
            prefix = 'SN',
            natart = solution.ingredient.art_nati,
            label_type = "Solution",
            pinnumber = solution.ingredient.id,
            approved = True,
        )
        new_flavor.save()

        base_formula = Formula(
            flavor = new_flavor,
            ingredient = base,
            amount = 1000 * (Decimal(solution.percentage) / 100) #percentage is a Decimal int eg. Decimal('10.00') to represent 10%
        )
        base_formula.save()

        solvent_formula = Formula(
            flavor = new_flavor,
            ingredient = solvent,
            amount = 1000 * ((100 - Decimal(solution.percentage))/100)
        )
        solvent_formula.save()

        recalculate_guts(new_flavor)

        #set the ingredient to have a sub_flavor which allows the newly created flavor-solution to be used in formulas in its place
        ingredient.sub_flavor = new_flavor
        ingredient.save()

        #solution.delete() #Is there any tracability if something screws up with the conversion?  Should I delete after converting?  Are there any repercussions for not deleting the solution
