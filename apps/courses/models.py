from django.db import models

from apps.authentication.models import User


class Course(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=319, blank=True, null=True)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}->{self.title}"


class Topic(models.Model):
    course = models.ForeignKey(Course, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=319, blank=True, null=True)
    index = models.IntegerField(default=0, blank=True, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"
