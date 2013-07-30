"""
Describes all of the data related to HACCP forms and logs 
"""


from django.db import models
from django.contrib.auth.models import User
from access.models import Customer, Flavor

class CustomerComplaint(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer)
    flavor_object = models.ForeignKey(Flavor,blank=True,null=True)
    flavor_number = models.PositiveIntegerField()
    lot = models.PositiveIntegerField()
    description = models.TextField()
    conclusion = models.TextField()
    
    def __unicode__(self):
        return "%s -- %s -- %s" % (self.date.date(), self.customer, self.description[:50])
    
    def save(self, *args, **kwargs):
        try:
            self.flavor_object = Flavor.objects.get(number=self.flavor_number)
        except:
            pass
        super(CustomerComplaint, self).save(*args, **kwargs)

class CorrectiveAction(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, blank=True, null=True)
    description = models.TextField("Description of Occurrence")    
    root_cause = models.TextField()
    recommendations = models.TextField()
    action_plan = models.TextField()
    validation = models.TextField()
    comments = models.TextField(blank=True)
    
    def __unicode__(self):
        return "%s -- %s -- %s" % (self.date.date(), self.customer, self.description[:50])
    
class CIPM(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    recommendations = models.TextField()
    action_plan = models.TextField()
    validation = models.TextField()
    comments = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Continuous Improvement and Preventative Maintenance"
        verbose_name_plural = "CIPMs"
        
    def __unicode__(self):
        return "%s -- %s" % (self.date.date(), self.description[:50])

class WaterTest(models.Model):
    test_date = models.DateField()
    zone = models.PositiveSmallIntegerField()
    test_result = models.DecimalField(max_digits=2, decimal_places=1)
    
    def __unicode__(self):
        return "%s - Zone #%s - %s" % (self.test_date, self.zone, self.test_result)
    
    class Meta:
        ordering = ['-test_date']
        
class QualityTest(models.Model):
    test_date = models.DateField()
    zone = models.PositiveSmallIntegerField()
    
    
    class Meta:
        ordering = ['-test_date']


class TobaccoBeetleTest(QualityTest):
    test_result = models.PositiveSmallIntegerField() #TODO change this to be more semantic or include some meta info
    
    def __unicode__(self):
        return "%s - Zone #%s - %s" % (self.test_date, self.zone, self.test_result)
    
class ThermometerTest(QualityTest):
    test_result = models.PositiveSmallIntegerField() #TODO change this to be more semantic or include some meta info
    
    def __unicode__(self):
        return "%s - Zone #%s - %s" % (self.test_date, self.zone, self.test_result)
    

###################################################

class KosherGroup(models.Model):
    name = models.CharField(max_length=2)

    def __unicode__(self):
        return self.name

class ReceivingLog(models.Model):
    entry_date = models.DateTimeField()
    receiving_number = models.PositiveIntegerField()
    pin_number = models.PositiveIntegerField()
    supplier_id = models.ForeignKey('Supplier')
    description_of_goods = models.CharField(max_length=50)
    package_quantity = models.PositiveIntegerField()
    supplier_lot_number = models.CharField(max_length=25)
    po_number = models.PositiveIntegerField()
    truck = models.CharField(max_length=25)
    kosher_group = models.ForeignKey('KosherGroup', blank=True, null=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.entry_date.year)[2:5] + "-R" + str(self.receiving_number) + " - Pin #" + str(self.pin_number) + " - " + self.description_of_goods + " - " + self.supplier_id.__unicode__()

class Supplier(models.Model):
    id = models.IntegerField(primary_key=True)
    supplier_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.supplier_name

    class Meta:
        ordering = ['supplier_name']
        db_table = u'supplier'
