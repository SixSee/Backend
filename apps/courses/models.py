from django.db import models

from apps.authentication.models import User


class Course(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    views = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}->{self.name}"
