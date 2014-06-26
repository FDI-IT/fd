from django.db import models

from access.models import Flavor

# Create your models here.
class ApplicationType(models.Model):
    name = models.CharField(max_length=40)   
    def __unicode__(self):
        return self.name
    
class Application(models.Model):
    # add a foreign key to productinfo from unified adpater
    flavor = models.ForeignKey(Flavor)
    application_type = models.ForeignKey('ApplicationType')
    usage_level = models.DecimalField('Starting Usage level (percentage) (required)', decimal_places=3,
                                      max_digits=5)
    top_usage_level = models.DecimalField('Top Usage Level (percentage) (optional)', decimal_places=3,
                                      max_digits=5, blank=True, null=True)
    memo = models.TextField(blank=True)
    added_from_spreadsheet = models.BooleanField(default=False,blank=True)
    original_spreadsheet_fields = models.CharField(max_length=100,default="",blank=True)
    def get_admin_url(self):
        return "/admin/flavor_usage/application/%s/" % self.pk
    
    def __unicode__(self):
        if self.top_usage_level:
            return u"%s: %s %s-%s%%" % (self.flavor, self.application_type, self.usage_level, self.top_usage_level)
        else:
            return u"%s: %s %s%%" % (self.flavor, self.application_type, self.usage_level)
        
        
    @property
    def short_memo(self):
        if len(self.memo) > 20:
            return u"%s..." % self.memo[:20]
        else:
            return self.memo