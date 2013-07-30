from django.db import models

class Flavors(models.Model):
        flavor_id = models.PositiveIntegerField("'product number,' 'flavor number,' etc in FD nomenclature",\
                                                primary_key=True)
        name = models.CharField("Name of the flavor",max_length=100)
        prefix = models.CharField("Prefix of the flavor id. Typically an abbreviation of the name",\
                                  max_length=2)
        appearance = models.CharField("Description of the appearance of the finished product",\
                                      max_length=100,blank=True)
        organoleptic = models.CharField("Description of the organoleptic propertiesof the finished product",\
                                        max_length=100,blank=True)
        testing_procedure = models.CharField("Procedure to QC the flavor", max_length=255,blank=True)
        flash_point = models.FloatField(blank=True)
        specific_gravity = models.FloatField(blank=True)

        def __unicode__(self):
                return self.prefix + "-" + self.flavor_id + " | " + self.name


class QC(models.Model):
      retain = models.PositiveSmallIntegerField("Retain index number")
      date = models.DateField("Date on which product was QCed")
      lot = models.PositiveIntegerField("Lot number, assigned in production")
      passed = models.BooleanField("True if this product passed QC", default=True)
      amount = FloatField("The amount, in pounds, of product that was sent with this lot number")
      notes = models.CharField("Notes from the QC test",max_length=255)
      flavor_id = models.ForeignKey("The flavor which was QCed")

      def __unicode__(self):
              return self.retain + " | " + self.date + " | flavor: " + self.flavor_id
