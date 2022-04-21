# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Course, Topic, CourseReview


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'description',
        'owner',
        'is_archived',
        'created_at',
        'updated_at',
    )
    list_filter = ('owner', 'is_archived', 'created_at', 'updated_at')
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
        'text',
        'created_at',
        'updated_at',
    )
    list_filter = ('course', 'created_at', 'updated_at')
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