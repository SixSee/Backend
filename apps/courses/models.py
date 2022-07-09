from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from Excelegal.helpers import UploadTo, validate_image
from apps.authentication.models import User


class Course(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=319, blank=True, null=True)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to=UploadTo('course_images'), validators=[validate_image], blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}->{self.title}"

    def get_image_url(self):
        return self.image.url

    def get_avg_rating(self) -> int:
        ratings = list(self.reviews.all().values_list('rating'))
        ratings = [i[0] for i in ratings]
        if ratings:
            return round(sum(ratings) / len(ratings))
        return 0


class Topic(models.Model):
    course = models.ForeignKey(Course, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=319, blank=True, null=True)
    index = models.CharField(max_length=100, default="0", blank=True, null=True)
    text = models.TextField()
    footnote = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class CourseReview(models.Model):
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    review_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
