from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

import apps.courses.models
from Excelegal.dao import dao_handler
from Excelegal.helpers import respond
from .models import Course, Topic, CourseReview
from .serializers import TopicSerializer, CourseReviewSerializer


class CourseViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    class OutputSerializer(serializers.ModelSerializer):
        topics = TopicSerializer(many=True)
        reviews = CourseReviewSerializer(many=True)

        class Meta:
            model = Course
            fields = ['id', 'title', 'is_archived', 'image', 'slug', 'description', 'topics', 'reviews']

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
        description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        image = serializers.ImageField(required=False, allow_null=False, allow_empty_file=False)
        is_archived = serializers.BooleanField(required=False, allow_null=False)

    def list(self, request):
        user = request.user
        # todo-> seperate apis for getting courses for main site or admin panel?
        if not user.is_anonymous and user.isAdmin():
            courses = Course.objects.order_by('id').all()
        else:
            courses = Course.objects.filter(is_archived=False, is_live=True).order_by('id').all()
        serializer = self.OutputSerializer(courses, many=True)
        return respond(200, "Success", serializer.data)

    def retrieve(self, request, slug=None):
        user = request.user
        course = Course.objects.filter(slug=slug).first()
        serializer = self.OutputSerializer(course)
        return respond(200, "Success", serializer.data)

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
            dao_handler.course_dao.save_from_dict(serializer.validated_data, course)
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
            topic_index_exists = (Topic.objects
                                  .filter(course__slug=course_slug, index=index)
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
                dao_handler.topic_dao.shift_topics_down(index, topic.course)
            dao_handler.topic_dao.save_from_dict(serializer.validated_data, topic)
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


class CourseReviewView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = CourseReview
            fields = ['id', 'review_by', 'text', 'rating', 'created_at', 'updated_at']

    class InputSerializer(serializers.Serializer):
        text = serializers.CharField(required=False, allow_blank=True)
        rating = serializers.IntegerField(required=True, min_value=0, max_value=5)

    def get(self, request, course_slug=None, format=None):
        course = dao_handler.course_dao.get_by_slug(course_slug)
        if not course:
            return respond(200, "No course with this slug")
        reviews = course.coursereview_set.all()
        serializer = self.OutputSerializer(reviews, many=True)
        return respond(200, "Success", serializer.data)

    def post(self, request, course_slug=None):
        body = request.data
        user = request.user
        course = dao_handler.course_dao.get_by_slug(course_slug)

        if not course:
            return respond(200, "No course with this slug")
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Fail", serializer.errors)

        serializer.validated_data['review_by'] = user if not user.is_anonymous else None
        serializer.validated_data['course'] = course
        dao_handler.course_review_dao.create_review(**serializer.validated_data)
        return respond(200, "Success")

    def put(self, request, course_slug=None):
        body = request.data
        user = request.user

        course = dao_handler.course_dao.get_by_slug(course_slug)
        if not course:
            return respond(200, "No course with this slug")
        pk = request.GET.get('id', None)
        review: apps.courses.models.CourseReview = dao_handler.course_review_dao.get_by_id(id=pk)
        if not review:
            return respond(400, "No review found with this id")
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Fail", serializer.errors)
        if user.id != review.review_by.id:
            return respond(400, "This review doesn't belong to you")

        dao_handler.course_review_dao.save_from_dict(serializer.validated_data, review)
        return respond(200, "Success")
