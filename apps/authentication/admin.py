from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'is_email_verified',
        'from_google',
        'last_login',
        'id',
        'password',
        'is_superuser',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
        'username',
    )
    list_filter = (
        'last_login',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'is_email_verified',
    )
    raw_id_fields = ('groups', 'user_permissions')
    date_hierarchy = 'date_joined'
