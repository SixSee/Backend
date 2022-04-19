import random
import string

from django.utils.text import slugify


def unique_slug_generator(instance, keyword, new_slug=None):
    """
    This is for a Django project, and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """

    def random_string_generator(size=5, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    if not new_slug :
        slug = new_slug
    else:
        slug = slugify(keyword)
    slug_exists = instance.objects.filter(slug=slug).exists()
    if slug_exists:
        slug = f"{slug}-{random_string_generator(size=3)}"
    return slug
