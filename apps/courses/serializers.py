from rest_framework import serializers

from .models import Topic, CourseReview


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title', 'slug', 'index', 'text']
        extra_kwargs = {
            'id': {'read_only': True},
        }


class CourseReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = ['id', 'review_by', 'text', 'rating', 'created_at', 'updated_at']
