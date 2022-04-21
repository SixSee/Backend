from django.db import models

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
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=15, choices=BlogTypes.choices, default=BlogTypes.Blog)
    is_live = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_type(self):
        return self.BlogTypes[self.type]

    def __str__(self):
        return f"{self.title[:10]}->{self.type}->{self.owner.email}"
