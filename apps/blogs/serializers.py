from rest_framework import serializers

from .models import Blog, BlogReview


class BlogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'


class BlogReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogReview
        fields = ['id', 'review_by', 'text', 'rating', 'created_at', 'updated_at']

