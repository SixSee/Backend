from django.db import models
from apps.authentication.models import User
from Excelegal.helpers import validate_image, UploadTo


class Bulletin(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=319)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=UploadTo('bulletin_images'), validators=[validate_image], blank=True, null=True)
    description = models.TextField()
    # category = models.CharField(max_length=127)
    # action_title = models.CharField(max_length=255, default="")
    # action_link = models.URLField(max_length=511)
    visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
