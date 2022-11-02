# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Bulletin


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'owner',
        'image',
        'description',
        'visible',
        'created_at',
        'updated_at',
        'id',
    )
    list_filter = ('owner', 'visible', 'created_at', 'updated_at')
    search_fields = ('slug',)
    date_hierarchy = 'created_at'
