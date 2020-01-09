from django.db import models
from reversion.models import Version

# Create your models here.

class FDIVersion(Version):
    def get_absolute_url(self):
        pass