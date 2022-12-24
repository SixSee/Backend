import re

from django.http import HttpResponse, HttpResponseNotFound
from ebooklib import epub
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

import apps.courses.models
from Excelegal.dao import dao_handler
from Excelegal.helpers import respond
from apps.authentication.serializers import UserSerializer
from .helpers import get_latest_courses, style as style2
from .models import Course, Topic, CourseReview
from .serializers import CourseReviewSerializer


class CourseViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    class OutputSerializer(serializers.ModelSerializer):
        reviews = CourseReviewSerializer(many=True)

        class Meta:
            model = Course
            fields = ['id', 'title', 'is_archived', 'image', 'slug', 'description', 'reviews', 'is_approved']
            depth = 1

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
        description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        image = serializers.ImageField(required=False, allow_null=False, allow_empty_file=False)
        is_archived = serializers.BooleanField(required=False, allow_null=False)

    def list(self, request):
        user = request.user
        if not user.is_anonymous and user.isAdmin():
            courses = Course.objects.order_by('id').all()
        else:
            courses = Course.objects.filter(is_archived=False, is_approved=True).order_by('id').all()
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
        course = Course.objects.create(owner=user, **serializer.validated_data)
        return respond(200, "Success")

    def update(self, request, slug=None):
        user = request.user
        body = request.data
        course = Course.objects.filter(slug=slug).first()

        if not course:
            return respond(400, "No course with this slug")

        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(200, "Fail", serializer.errors)
        dao_handler.course_dao.save_from_dict(serializer.validated_data, course)
        return respond(200, "Success")

    def destroy(self, request, slug=None):
        course = Course.objects.filter(slug=slug).first()
        user = request.user

        if not course:
            return respond(400, "No course with this slug")

        course.delete()
        return respond(200, "Success")

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_course(self, request, slug=None):
        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")

        course = Course.objects.filter(slug=slug).first()
        if not course:
            return respond(400, "No course with this slug")
        course.is_approved = not course.is_approved
        course.save()
        return respond(200, "Success")


class CourseTopicViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'topic_slug'

    def _human_key(self, key):
        parts = re.split('(\d*\.\d+|\d+)', key)
        return tuple((e.swapcase() if i % 2 == 0 else float(e))
                     for i, e in enumerate(parts))

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=True)
        index = serializers.CharField(required=True)
        text = serializers.CharField(required=True)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Topic
            exclude = ['course']

    def list(self, request, course_slug=None):
        topics = Topic.objects.filter(course__slug=course_slug, course__is_archived=False).all()
        topics = list(topics)
        topics.sort(key=lambda x: self._human_key(x.index))
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
        dao_handler.topic_dao.save_from_dict(serializer.validated_data, topic)
        return respond(200, "Success")

    def destroy(self, request, course_slug=None, topic_slug=None):
        user = request.user
        topic = Topic.objects.filter(slug=topic_slug, course__slug=course_slug).first()
        if not topic:
            return respond(200, "No topic with this slug")
        topic.delete()
        return respond(200, "Success")


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
            return respond(404, "No course with this slug")
        reviewAlready = CourseReview.objects.filter(course=course, review_by=user).first()
        if reviewAlready:
            return respond(400, "Only one review allowed per user")
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


class LatestCoursesView(APIView):
    permission_classes = [AllowAny]

    class OutputSerializer(serializers.ModelSerializer):
        avg_rating = serializers.SerializerMethodField()
        owner = UserSerializer()
        reviews = CourseReviewSerializer(many=True)

        class Meta:
            model = Course
            fields = ('title', 'slug', 'reviews', 'avg_rating', 'owner', 'image', 'description')

        def get_avg_rating(self, instance):
            return instance.get_avg_rating()

    def get(self, request):
        serializer = self.OutputSerializer(get_latest_courses(), many=True)
        return respond(200, "Success", serializer.data)


class CourseEPUBView(APIView):

    def get(self, request, course_slug=None):
        course = dao_handler.course_dao.get_by_slug(course_slug)
        if not course:
            return respond(400, "No course with this slug")
        topics = course.topics.order_by('index').all()
        if topics.count() == 0:
            return respond(400, "No topics")
        book = epub.EpubBook()
        book.set_title(course.title)
        style = '''BODY { text-align: justify;}'''

        default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css",
                                    content=style)
        book.add_item(default_css)
        chapters = []
        for topic in topics:
            # create chapter
            if topic.text == "":
                continue
            c = epub.EpubHtml(title=topic.title, file_name=f"{topic.slug}.xhtml", lang='hr')
            c.content = f"<h1>{topic.title}</h1>" + topic.text
            book.add_item(c)
            chapters.append(c)
        book.toc = tuple(chapters)
        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style2)
        book.add_item(nav_css)

        spine = chapters
        book.spine = spine
        epub_location = f"./Excelegal/media/epub_courses/{course.slug}.epub"
        epub.write_epub(epub_location, book, {})
        try:
            with open(epub_location, "rb") as file:
                data = file.read()
            response = HttpResponse(data)
            response['Content-Disposition'] = f'attachment; filename="{course.slug}.epub"'
        except IOError:
            response = HttpResponseNotFound('<h1>File not exist</h1>')
        return response
