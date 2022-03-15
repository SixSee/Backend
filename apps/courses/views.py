from datetime import datetime

from rest_framework import status as s, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.authentication.models import User
from .models import Course, Topic


class CreateCourseViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Course
            exclude = ['created_at', 'updated_at', 'owner', 'views', 'is_archived']

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=True)
        description = serializers.CharField(required=True)

    def list(self, request):
        user = request.user

        if user.isAdmin():
            courses = Course.objects.all()
        elif user.isStaff():
            courses = Course.objects.filter(owner=user, is_archived=False)
        else:
            return Response({"msg": "invalid perms"}, s.HTTP_400_BAD_REQUEST)
        serializer = self.OutputSerializer(courses, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        course = Course.objects.filter(pk=pk).first()
        serializer = self.OutputSerializer(course)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        body = request.data
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return Response(serializer.errors, s.HTTP_400_BAD_REQUEST)

        if "owner" in body.keys() and user.isAdmin():
            course_owner_uuid = body.get('owner')
            course_owner = User.objects.filter(pk=course_owner_uuid).first()
            if course_owner is None:
                return Response({"msg": "no user with this id"}, status=s.HTTP_400_BAD_REQUEST)

            course = Course(owner=course_owner, **serializer.data)

        elif user.isStaff():
            course = Course(owner=user, **serializer.data)
        else:
            return Response({"msg": "invalid perms"}, s.HTTP_400_BAD_REQUEST)

        course.save()
        return Response(serializer.data, s.HTTP_201_CREATED)

    def update(self, request, pk=None):
        user = request.user
        course = Course.objects.filter(pk=pk).first()
        if not course:
            return Response({'msg': 'No course with this id'}, s.HTTP_400_BAD_REQUEST)

        body = request.data
        if course.owner == user or user.isAdmin():
            course.title = body.get('title', course.title)
            course.description = body.get('description', course.description)
            course.updated_at = datetime.now()
            course.save()
        else:
            return Response({"msg": "Invalid perms"}, s.HTTP_400_BAD_REQUEST)
        return Response({"msg": "Updated"}, s.HTTP_200_OK)

    def destroy(self, request, pk=None):
        course = Course.objects.filter(pk=pk).first()
        user = request.user
        if not course:
            return Response({'msg': 'No course with this id'}, s.HTTP_400_BAD_REQUEST)

        if course.owner == user or user.isAdmin():
            course.delete()
        else:
            return Response({"msg": "Invalid perms"}, s.HTTP_400_BAD_REQUEST)
        return Response({"msg": "updated"}, s.HTTP_200_OK)


class CreateCourseTopicViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=True)
        index = serializers.IntegerField(required=True)
        text = serializers.CharField(required=True)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Topic
            exclude = ['slug', 'id', 'course']

    def list(self, request, course_pk=None):
        user = request.user
        topics = Topic.objects.filter(course=course_pk).order_by('index')
        serializer = self.OutputSerializer(topics, many=True)
        return Response(serializer.data, s.HTTP_200_OK)

    def retrieve(self, request, pk=None, course_pk=None):
        user = request.user
        topic = Topic.objects.filter(pk=pk, course=course_pk).first()
        if topic:
            serializer = self.OutputSerializer(topic)
            return Response(serializer.data, s.HTTP_200_OK)
        return Response({"msg": "No topic with this id"}, s.HTTP_400_BAD_REQUEST)

    def create(self, request, course_pk=None):
        user = request.user
        body = request.user
        course = Course.objects.filter(pk=course_pk).first()
        if course is None:
            return Response({"msg": "No topic with this id"}, s.HTTP_400_BAD_REQUEST)
        if course.owner == user or user.isAdmin():
            serializer = self.InputSerializer(data=body)
            if not serializer.is_valid():
                return Response(serializer.errors, s.HTTP_400_BAD_REQUEST)
            print(serializer.data)
            topic = Topic(course=course, **serializer.data)
            topic.save()
        return Response(s.HTTP_201_CREATED)

    def update(self, request, course_pk=None, pk=None):
        user = request.user
        topic = Topic.objects.filter(pk=pk, course_id=course_pk).first()
        if not topic:
            return Response({'msg': 'No topic with this id'}, s.HTTP_400_BAD_REQUEST)
        body = request.data
        if topic.course.owner == user or user.isAdmin():
            topic.title = body.get('title', topic.title)
            topic.text = body.get('text', topic.text)
            topic.index = body.get('index', topic.index)
            topic.save()
        else:
            return Response({"msg": "Invalid perms"}, s.HTTP_400_BAD_REQUEST)
        return Response({"msg": "Updated"}, s.HTTP_200_OK)

    def destroy(self, request, course_pk=None, pk=None):
        user = request.user
        topic = Topic.objects.filter(pk=pk, course_id=course_pk).first()
        if not topic:
            return Response({'msg': 'No topic with this id'}, s.HTTP_400_BAD_REQUEST)
        if topic.course.owner == user or user.isAdmin():
            topic.delete()
        else:
            return Response({"msg": "Invalid perms"}, s.HTTP_400_BAD_REQUEST)
        return Response({"msg": "updated"}, s.HTTP_200_OK)

