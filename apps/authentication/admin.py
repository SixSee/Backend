# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'password',
        'last_login',
        'is_superuser',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
        'id',
        'username',
        'email',
        'is_email_verified',
        'from_google',
        'access_token',
        'device_id',
        'role',
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
