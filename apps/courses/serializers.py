from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from .models import Topic, CourseReview


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title', 'slug', 'index', 'text', 'footnote']
        extra_kwargs = {
            'id': {'read_only': True},
        }


class CourseReviewSerializer(serializers.ModelSerializer):
    review_by = UserSerializer()

    class Meta:
        model = CourseReview
        fields = ['id', 'review_by', 'text', 'rating', 'created_at', 'updated_at']
