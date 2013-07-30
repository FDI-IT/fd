from django.db import models
from access.models import Ingredient

# Create your models here.
class Solution(models.Model):
    ingredient = models.OneToOneField(Ingredient, related_name='ing_obj', db_index=True)
    my_base = models.ForeignKey(Ingredient, null=True, blank=True, related_name='my_base', db_index=True)
    my_solvent = models.ForeignKey(Ingredient, null=True, blank=True, related_name='my_solvent', db_index=True)
    percentage = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    status = models.ForeignKey('SolutionStatus', blank=True, null=True)
    
    def __unicode__(self):
        return "%s - %s %s %s" % (self.ingredient.id,
                                   self.ingredient.art_nati,
                                   self.ingredient.prefix,
                                   self.ingredient.product_name)
    
    class Meta:
        ordering = ['ingredient']
        
class SolutionStatus(models.Model):
    status_name = models.CharField(max_length=20)
    status_order = models.PositiveSmallIntegerField()
    
    def __unicode__(self):
        return "%s" % (self.status_name)
    
    class Meta:
        ordering = ['status_order']
        
class SolutionMatchCache(models.Model):
    my_pk = models.AutoField(primary_key=True)
    id = models.IntegerField()
    value = models.IntegerField()
    label = models.CharField(max_length=150)
    solution = models.ForeignKey('Solution')

    
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