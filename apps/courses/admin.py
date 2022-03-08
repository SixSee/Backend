from django.contrib import admin

from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'views',
        'owner',
        'created_at',
        'updated_at',
    )
    list_filter = ('owner', 'created_at', 'updated_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'