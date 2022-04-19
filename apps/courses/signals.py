from django.db.models.signals import pre_save
from django.dispatch import receiver

from .helpers import unique_slug_generator
from .models import Course, Topic


@receiver(pre_save, sender=Course)
def set_slug_course(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(Course, instance.title)

    prev_instance = Course.objects.filter(pk=instance.pk).first()

    if prev_instance and prev_instance.title is not instance.title:
        instance.slug = unique_slug_generator(Course, instance.title)


@receiver(pre_save, sender=Topic)
def set_slug_topic(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(Topic, instance.title)

    prev_instance = Topic.objects.filter(pk=instance.pk).first()

    if prev_instance and prev_instance.title is not instance.title:
        instance.slug = unique_slug_generator(Topic, instance.title)
