from django.db import models

from apps.authentication.models import User


class ScheduleClass(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=319)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting_id = models.CharField(max_length=319)
    meeting_at = models.DateTimeField()
    duration = models.IntegerField(verbose_name='Duration in minutes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
