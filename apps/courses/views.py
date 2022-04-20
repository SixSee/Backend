from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from Excelegal.dao import dao_handler
from Excelegal.helpers import respond
from .models import Course, Topic
from .serializers import TopicSerializer


class CourseViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    class OutputSerializer(serializers.ModelSerializer):
        topics = TopicSerializer(many=True)

        class Meta:
            model = Course
            exclude = ['created_at', 'updated_at', 'owner', 'is_archived']

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
        description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def list(self, request):
        user = request.user
        # todo-> seperate apis for getting courses for main site or admin panel?
        if not user.is_anonymous and user.isAdmin:
            courses = Course.objects.all()
        else:
            courses = Course.objects.filter(is_archived=False)
        serializer = self.OutputSerializer(courses, many=True)
        return respond(200, "Success", serializer.data)

    # todo _> Continue from here
    def retrieve(self, request, slug=None):
        user = request.user
        course = Course.objects.filter(slug=slug).first()
        serializer = self.OutputSerializer(course)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        body = request.data
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(200, "Fail", serializer.errors)
        if user.isStudent():
            return respond(200, "You dont have permission to create courses")
        course = dao_handler.course_dao.create_course(**serializer.validated_data, owner=user)
        return respond(200, "Success")

    def update(self, request, slug=None):
        user = request.user
        body = request.data
        course = Course.objects.filter(slug=slug).first()

        if not course:
            return respond(400, "No course with this slug")

        if course.owner == user or user.isAdmin():
            serializer = self.InputSerializer(data=body)
            if not serializer.is_valid():
                return respond(200, "Fail", serializer.errors)
            course.title = serializer.validated_data.get('title', course.title)
            course.description = serializer.validated_data.get('description', course.description)
            course.updated_at = timezone.now()
            course.save()
            return respond(200, "Success")
        else:
            return respond(400, "You dont have permission")

    def destroy(self, request, slug=None):
        course = Course.objects.filter(slug=slug).first()
        user = request.user

        if not course:
            return respond(400, "No course with this slug")

        if course.owner == user or user.isAdmin():
            course.delete()
            return respond(200, "Success")
        else:
            return respond(400, "You dont have permission")


class CourseTopicViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'topic_slug'

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=True)
        index = serializers.IntegerField(required=True)
        text = serializers.CharField(required=True)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Topic
            exclude = ['course']

    def list(self, request, course_slug=None):
        user = request.user
        topics = Topic.objects.filter(course__slug=course_slug, course__is_archived=False).order_by('index')
        serializer = self.OutputSerializer(topics, many=True)
        return respond(200, "Success", serializer.data)

    def retrieve(self, request, topic_slug=None, course_slug=None):
        user = request.user
        topic = Topic.objects.filter(slug=topic_slug, course__slug=course_slug, course__is_archived=False).first()
        if not topic:
            return respond(400, "No topic with this id")
        serializer = self.OutputSerializer(topic)
        return respond(200, "Success", serializer.data)

    def create(self, request, course_slug=None):
        user = request.user
        body = request.data
        course = Course.objects.filter(slug=course_slug).first()

        if not course:
            return respond(200, "No topic with this slug")

        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(200, "Failure", serializer.errors)

        if course.owner == user or user.isAdmin():
            # Check if index does not exists previously
            index = serializer.validated_data.get('index')
            topic_index_exists = (Topic.objects.
                                  filter(course__slug=course_slug, index=index)
                                  .exists())
            if topic_index_exists:
                # shift down other topics
                dao_handler.topic_dao.shift_topics_down(index, course)

            topic = dao_handler.topic_dao.create_topic(course=course, **serializer.validated_data)
            return respond(200, "Success")
        else:
            return respond(400, "You dont have permission")

    def update(self, request, course_slug=None, topic_slug=None):
        user = request.user
        body = request.data
        topic = Topic.objects.filter(slug=topic_slug, course__slug=course_slug).first()
        if not topic:
            return respond(200, "No topic with this slug")

        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(200, "Failure", serializer.errors)

        if topic.course.owner is user or user.isAdmin():
            # Check if index does not exists previously
            index = serializer.validated_data.get('index')
            topic_index_exists = (Topic.objects.
                                  filter(course__slug=course_slug, index=index)
                                  .exists())
            if topic_index_exists:
                # shift down other topics
                dao_handler.topic_dao.shift_topics_down(index, course)
            topic.title = serializer.validated_data.get('title', topic.title)
            topic.text = serializer.validated_data.get('text', topic.text)
            topic.index = serializer.validated_data.get('index', topic.index)
            topic.save()
            return respond(200, "Success")
        else:
            return respond(400, "You dont have permission")

    def destroy(self, request, course_slug=None, topic_slug=None):
        user = request.user
        topic = Topic.objects.filter(slug=topic_slug, course__slug=course_slug).first()
        if not topic:
            return respond(200, "No topic with this slug")
        if topic.course.owner == user or user.isAdmin():
            topic.delete()
            return respond(200, "Success")
        else:
            return respond(400, "You dont have permission")
