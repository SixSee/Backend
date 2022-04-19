from rest_framework import serializers

from .models import Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title', 'slug', 'index', 'text']
        extra_kwargs = {
            'id': {'read_only': True},
        }
