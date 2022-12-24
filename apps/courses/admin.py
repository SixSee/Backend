# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Course, Topic, CourseReview


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'is_archived',
        'is_approved',
        'owner',
        'image',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'owner',
        'is_archived',
        'is_approved',
        'created_at',
        'updated_at',
    )
    search_fields = ('slug',)
    date_hierarchy = 'created_at'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'course',
        'title',
        'slug',
        'index',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('course',)
    search_fields = ('slug',)
    date_hierarchy = 'created_at'


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'course',
        'review_by',
        'text',
        'rating',
        'created_at',
        'updated_at',
    )
    list_filter = ('course', 'review_by', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'