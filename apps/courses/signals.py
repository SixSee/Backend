import random
import string

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Course


# TODO:USE DJANGO CELERY INSTEAD OF SIGNALS

@receiver(pre_save, sender=Course)
def set_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


def random_string_generator(size=5, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.DisplayName)

    Klass = instance.__class__
    slug_exists = Klass.objects.filter(slug=slug).exists()
    if slug_exists:
        new_slug = f"{slug}-{random_string_generator(size=3)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
