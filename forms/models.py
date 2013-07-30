from django.db import models

# Create your models here.

class MeetingLog(models.Model):
    date = models.DateField()
    attendees = models.TextField()
    meeting_type = models.TextField()
    topic = models.TextField()
    conclusions = models.TextField()
    action_items = models.TextField()
    signatures = models.TextField()


