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
    ADMIN = 3
    MENTOR = 2
    STUDENT = 1

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MENTOR, 'Mentor'),
        (STUDENT, 'Student'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=1, blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "authentication"

    def __str__(self):
        return f"User:{self.email}"

    def is_student(self):
        return self.role == 1

    def is_mentor(self):
        return self.role == 2

    def is_admin(self):
        return self.is_superuser or self.role == 3
