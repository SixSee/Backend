from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from .models import Blog, BlogReview


class BlogReviewSerializer(serializers.ModelSerializer):
    review_by = UserSerializer()

    class Meta:
        model = BlogReview
        fields = ['id', 'review_by', 'text', 'rating', 'created_at', 'updated_at']


class BlogsSerializer(serializers.ModelSerializer):
    reviews = BlogReviewSerializer(many=True)
    owner = UserSerializer()

    class Meta:
        model = Blog
        fields = '__all__'
