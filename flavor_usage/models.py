from django.db import models

from access.models import Flavor

# Create your models here.
class ApplicationType(models.Model):
    name = models.CharField(max_length=40)
    def __str__(self):
        return self.name

class Application(models.Model):
    flavor = models.ForeignKey(Flavor, related_name="applications",on_delete=models.CASCADE)
    application_type = models.ForeignKey('ApplicationType',on_delete=models.CASCADE)

    # tag = models.ForeignKey('Tag')
    usage_level = models.DecimalField('Starting Usage level (percentage) (required)', decimal_places=3,
                                      max_digits=5)
    top_usage_level = models.DecimalField('Top Usage Level (percentage) (optional)', decimal_places=3,
                                      max_digits=5, blank=True, null=True)
    memo = models.TextField(blank=True)
    added_from_spreadsheet = models.BooleanField(default=False,blank=True)
    original_spreadsheet_fields = models.CharField(max_length=100,default="",blank=True)
    def get_admin_url(self):
        return "/admin/flavor_usage/application/%s/" % self.pk

    def __str__(self):
        if self.top_usage_level:
            return "%s: %s %s-%s%%" % (self.flavor, self.application_type, self.usage_level, self.top_usage_level)
        else:
            return "%s: %s %s%%" % (self.flavor, self.application_type, self.usage_level)


    @property
    def short_memo(self):
        if len(self.memo) > 20:
            return "%s..." % self.memo[:20]
        else:
            return self.memo

class Tag(models.Model):
    # application_type = models.ForeignKey('ApplicationType')
    name = models.CharField(max_length=100)
    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)

    class Meta:
        unique_together=('name','flavor')

    def __str__(self):
        return "%s: %s" % (self.flavor, self.name)
