from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from Excelegal.helpers import validate_image, UploadTo
from apps.authentication.models import User


class Blog(models.Model):
    class BlogTypes(models.TextChoices):
        Blog = "blog", _("Blog")
        Workshop = "workshop", _("Workshop")
        Page = "page", _("Page")
        Competition = "competition", _("Competition")

    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=319, blank=True, null=True)
    text = models.TextField()
    image = models.ImageField(upload_to=UploadTo('blog_images'), validators=[validate_image], blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=15, choices=BlogTypes.choices, default=BlogTypes.Blog)
    is_live = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_type(self):
        return self.BlogTypes[self.type]

    def get_image_url(self):
        return self.image.url

    def __str__(self):
        return f"{self.title[:10]}->{self.type}"

    def get_avg_rating(self) -> int:
        ratings = self.reviews.all().values_list('rating')
        if ratings:
            return round(sum(ratings) / len(ratings))
        return 0
    

class BlogReview(models.Model):
    blog = models.ForeignKey(Blog, related_name='reviews', on_delete=models.CASCADE)
    review_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
