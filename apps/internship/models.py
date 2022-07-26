from django.db import models
from apps.authentication.models import User
from Excelegal.helpers import UploadTo, validate_image

class Internship(models.Model):
    company_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=UploadTo('internship_images'), validators=[validate_image], blank=True,
                              null=True)
    duration = models.TimeField(blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    stipend = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AppliedInternship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_no = models.CharField(max_length=17)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
