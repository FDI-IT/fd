from django.db import models
from django.db.models import signals


from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extra information about users.
    """
    user = models.OneToOneField(User)
    initials = models.CharField(max_length=3)
    sort_user_columns = models.CharField(max_length=256,blank=True)
    user_columns = models.CharField(max_length=256,blank=True)
    force_password_change = models.BooleanField(blank=True)
    lot_paginate_by = models.IntegerField(blank=True,default=25)
    
    def __unicode__(self):
        return self.user.__unicode__()