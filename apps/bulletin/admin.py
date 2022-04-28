# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Bulletin


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'visible',
        'owner',
        'category',
        'action_title',
        'action_link',
        'created_at',
        'updated_at',
    )
    list_filter = ('owner', 'visible', 'created_at', 'updated_at')
    search_fields = ('slug',)
    date_hierarchy = 'created_at'
