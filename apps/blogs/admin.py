# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Blog, BlogReview


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'text',
        'image',
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


@admin.register(BlogReview)
class BlogReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'blog',
        'review_by',
        'text',
        'rating',
        'created_at',
        'updated_at',
    )
    list_filter = ('blog', 'review_by', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'