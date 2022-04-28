from django.db.models.signals import pre_save
from django.dispatch import receiver

from Excelegal.helpers import unique_slug_generator
from .models import Bulletin


@receiver(pre_save, sender=Blog)
def set_slug_bulletin(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(Blog, instance.title)

    prev_instance = Blog.objects.filter(pk=instance.pk).first()

    if prev_instance and prev_instance.title != instance.title:
        instance.slug = unique_slug_generator(Blog, instance.title)
