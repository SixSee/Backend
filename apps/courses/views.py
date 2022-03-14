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
        if user.role >= user.MENTOR:
            courses = Course.objects.all()
        else:
            courses = Course.objects.filter(owner=user, is_archived=False)
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

        if "owner" in body.keys():
            course_owner_uuid = body.get('owner')
            course_owner = User.objects.filter(pk=course_owner_uuid).first()
            if course_owner is None:
                return Response({"msg": "no user with this id"}, status=s.HTTP_400_BAD_REQUEST)

            if (course_owner is not None) and user.role >= user.MENTOR:
                course = Course(owner=course_owner, **serializer.data)
            else:
                course = Course(owner=user, **serializer.data)

        else:
            course = Course(owner=user, **serializer.data)
        course.save()

        return Response(serializer.data, s.HTTP_201_CREATED)

    def update(self, request, pk=None):
        user = request.user
        course = Course.objects.filter(pk=pk).first()
        if not course:
            return Response({'msg': 'No course with this id'}, s.HTTP_400_BAD_REQUEST)
        body = request.data
        if course.owner == user or user.role >= user.MENTOR:
            course.title = body.get('title', course.title)
            course.description = body.get('description', course.description)
            course.updated_at = datetime.now()
            course.save()
        else:
            return Response({"msg": "you dont have perms"}, s.HTTP_400_BAD_REQUEST)
        return Response({"msg": "Updated"}, s.HTTP_200_OK)

    def destroy(self, request, pk=None):
        course = Course.objects.filter(pk=pk).first()
        user = request.user
        if not course:
            return Response({'msg': 'No course with this id'}, s.HTTP_400_BAD_REQUEST)

        if course.owner == user or user.role >= user.MENTOR:
            course.delete()
        else:
            return Response({"msg": "you dont have perms"}, s.HTTP_400_BAD_REQUEST)
        return Response({"msg": "updated"}, s.HTTP_200_OK)


class CreateCourseTopicViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        course_id = serializers.CharField(max_length=255)
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
        return Response({"msg": "No topic with this id"})

    def create(self, request, course_pk=None):
        user = request.user
        body = request.user
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return Response(serializer.errors, s.HTTP_400_BAD_REQUEST)
        return Response(s.HTTP_201_CREATED)

    def update(self, request, course_pk=None, pk=None):
        pass

    def destroy(self, request, course_pk=None, pk=None):
        pass
