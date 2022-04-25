import os
import random
import string
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
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
    return slug


class GenericDao:
    model = None

    def get_by_id(self, id):
        return self.model.objects.filter(pk=id).first()

    def save_from_dict(self, data_dict: dict, instance):
        for attr, val in data_dict.items():
            setattr(instance, attr, val)
        return instance.save()


def validate_image(image):
    file_size = image.file.size
    limit_mb = 20
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError("Max size of file is %s MB" % limit)


@deconstructible
class UploadTo(object):

    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        extension = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid4().hex[:12], extension)
        return os.path.join(self.path, filename)
