# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'text',
        'owner',
        'type',
        'is_live',
        'is_archived',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'owner',
        'is_live',
        'is_archived',
        'created_at',
        'updated_at',
    )
    search_fields = ('slug',)
    date_hierarchy = 'created_at'