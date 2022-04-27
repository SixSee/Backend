import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    from_google = models.BooleanField(default=False)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    device_id = models.UUIDField(blank=True, null=True)
    ADMIN = 3
    STAFF = 2
    STUDENT = 1

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (STAFF, 'Staff'),
        (STUDENT, 'Student'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=1, blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "authentication"

    def __str__(self):
        return f"{self.id}"

    def isStudent(self):
        return self.role == 1

    def isStaff(self):
        return self.role == 2

    def isAdmin(self):
        return self.role == 3 or self.is_superuser
