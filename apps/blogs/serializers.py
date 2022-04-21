from rest_framework import serializers

from .models import Blog


class BlogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        exclude = ['is_live', 'is_archived', 'created_at', 'updated_at', 'is_archived', 'owner']
