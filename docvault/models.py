from datetime import date
import hashlib

from django.db import models
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic
from django.contrib.auth.models import User


class Doc(models.Model):
    """
    A scanned document.
    """
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    mailbox = models.PositiveSmallIntegerField(blank=True, default=0)
    
    class Meta:
        ordering = ['-date',]

    def __unicode__(self):
        return str(self.date.year)[2:5] + "-" + str(self.user)

    def get_admin_url(self):
        return "/admin/docvault/doc/%s" % self.pk
    
class Page(models.Model):
    doc = models.ForeignKey('Doc')
    image = models.ImageField(upload_to='docvault__page')
    hash = models.CharField(max_length=64)
    
    def save(self, *args, **kwargs):
        sha = hashlib.sha256()
        for chunk in iter(lambda: self.image.read(8192),''):
            sha.update(chunk)
        self.hash = sha.hexdigest()
        super(Page, self).save(*args, **kwargs)