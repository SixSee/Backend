import random
import string

from django.utils.text import slugify


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
        slug = slugify(instance.title)

    Klass = instance.__class__
    slug_exists = Klass.objects.filter(slug=slug).exists()
    if slug_exists:
        new_slug = f"{slug}-{random_string_generator(size=3)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
