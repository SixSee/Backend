from rest_framework import serializers

from .models import Blog


class BlogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'
