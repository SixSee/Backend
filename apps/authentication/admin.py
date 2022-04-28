# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'is_email_verified',
        'from_google',
        'role',
        'first_name',
        'last_name',
        'id',
        'password',
        'last_login',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'username',
        'access_token',
        'device_id',
    )
    list_filter = (
        'last_login',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'is_email_verified',
        'from_google',
    )
    raw_id_fields = ('groups', 'user_permissions')
