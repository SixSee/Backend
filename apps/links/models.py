from django.db import models


class Links(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    hyperlink = models.CharField(max_length=500, blank=True, null=True)
