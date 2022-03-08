from rest_framework import status as s, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Course


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
        courses = Course.objects.filter(owner=request.user, is_archived=False)
        print(courses)
        serializer = self.OutputSerializer(courses, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        course = Course.objects.filter(pk=pk, owner=request.user).first()
        if course:
            serializer = self.OutputSerializer(course)
            return Response(serializer.data)
        return Response({"msg": "error"}, )

    def create(self, request):
        body = request.data
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return Response({}, s.HTTP_400_BAD_REQUEST)
        course = Course(owner=request.user, **serializer.data)
        course.save()
        return Response(serializer.data, s.HTTP_201_CREATED)

    def update(self, request, pk=None):
        course = Course.objects.filter(pk=pk, owner=request.user).first()
        if not course:
            return Response({}, s.HTTP_400_BAD_REQUEST)
        body = request.data
        course.title = body.get('title', course.title)
        course.description = body.get('description', course.description)
        course.save()
        return Response(s.HTTP_200_OK)

    def destroy(self, request, pk=None):
        course = Course.objects.filter(pk=pk, owner=request.user).first()
        if not course:
            return Response({}, s.HTTP_400_BAD_REQUEST)
        course.delete()
        return Response({}, s.HTTP_200_OK)
