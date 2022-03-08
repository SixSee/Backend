from django.db import models

from apps.authentication.models import User


class Course(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=319, blank=True, null=True)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    views = models.BigIntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}->{self.title}"


class Topic(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=319, blank=True, null=True)
    index = models.IntegerField(default=0, blank=True, null=True)
    text = models.TextField()
    views = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True)
