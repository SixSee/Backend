from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Course, Topic
from .utils import unique_slug_generator


# TODO:USE DJANGO CELERY tasks to do SIGNALS

@receiver(pre_save, sender=Course)
def set_slug_course(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

    prev_instance = Course.objects.filter(pk=instance.pk).first()

    if (prev_instance is not None) and prev_instance.title is not instance.title:
        instance.slug = unique_slug_generator(instance)


@receiver(pre_save, sender=Course)
def set_slug_topic(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

    prev_instance = Topic.objects.filter(pk=instance.pk).first()

    if (prev_instance is not None) and (prev_instance.title is not instance.title):
        instance.slug = unique_slug_generator(instance)
