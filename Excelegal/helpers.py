import random
import string

from django.utils.text import slugify
from rest_framework.response import Response


def respond(status, message="", payload=False):
    response_json = {}
    if message:
        response_json['message'] = message
    if payload:
        response_json['payload'] = payload

    if bool(response_json) is False:
        raise Exception("Either message or payload is required")

    return Response(response_json, status=status)


def unique_slug_generator(instance, keyword, new_slug=None):
    """
    This is for a Django project, and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    def random_string_generator(size=5, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    if new_slug:
        slug = new_slug
    else:
        slug = slugify(keyword)
    if instance.objects.filter(slug=slug).exists():
        slug = f"{slug}-{random_string_generator(size=2)}"
    import pdb
    pdb.set_trace()
    return slug


class GenericDao:
    model = None

    def get_by_id(self, id):
        return self.model.objects.filter(pk=id).first()

    def save_from_dict(self, data_dict, pk=None):
        obj, created = self.model.objects.update_or_create(**data_dict)
        return obj, created
