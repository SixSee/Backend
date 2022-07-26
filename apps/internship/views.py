from django.shortcuts import render

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from .models import Internship, AppliedInternship
from apps.authentication.serializers import UserSerializer
from Excelegal.dao import dao_handler
from Excelegal.helpers import respond


class InternshipViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        created_by = UserSerializer()

        class Meta:
            model = Internship
            fields = ['id', 'image', 'company_name', 'duration', 'type', 'stipend', 'is_approved', 'created_at',
                      'updated_at', 'created_by']

    class InputSerializer(serializers.Serializer):
        company_name = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
        type = serializers.CharField(max_length=100, required=True)
        stipend = serializers.CharField(max_length=100)
        duration = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        image = serializers.ImageField(required=False, allow_null=False, allow_empty_file=False)

    def list(self, request):
        user = request.user
        if not user.is_anonymous and user.isAdmin():
            internship = Internship.objects.order_by('created_at').all()
        else:
            internship = Internship.objects.order_by('created_at').all()
        serializer = self.OutputSerializer(internship, many=True)
        return respond(200, "Success", serializer.data)

    def retrieve(self, request, id=None):
        user = request.user
        internship = Internship.objects.filter(pk=id).first()
        serializer = self.OutputSerializer(internship)
        return respond(200, "Success", serializer.data)

    def create(self, request):
        user = request.user
        body = request.data
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Fail", serializer.errors)
        if user.isStudent():
            return respond(200, "You dont have permission to create courses")
        internship = Internship(**serializer.validated_data, owner=user)
        return respond(200, "Success")

    def update(self, request, id=None):
        user = request.user
        body = request.data
        internship = Internship.objects.filter(pk=id).first()

        if not internship:
            return respond(400, "No course with this slug")

        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(200, "Fail", serializer.errors)
        dao_handler.internship_dao.save_from_dict(serializer.validated_data, internship)
        return respond(200, "Success")

    def destroy(self, request, id=None):
        internship = Internship.objects.filter(pk=id).first()
        user = request.user

        if not internship:
            return respond(400, "No course with this slug")

        internship.delete()
        return respond(200, "Success")

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_internship(self, request, id=None):
        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")

        internship = Internship.objects.filter(pk=id).first()
        if not internship:
            return respond(400, "No course with this slug")
        internship.is_approved = not internship.is_approved
        internship.save()
        return respond(200, "Success")


class LatestInternships(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        created_by = UserSerializer()

        class Meta:
            model = Internship
            fields = ['id', 'image', 'company_name', 'duration', 'type', 'stipend', 'is_approved', 'created_at',
                      'updated_at', 'created_by']

    permission_classes = [AllowAny]

    def get(self, request):
        internship = Internship.objects.filter(is_approved=True).order_by('-created_at').all()
        serializer = self.OutputSerializer(internship, many=True)
        return respond(200, "Success", serializer.data)


class ApplyInternshipView(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
        email = serializers.CharField(max_length=100, required=True)
        contact_no = serializers.CharField(max_length=20, required=True)
        description = serializers.CharField(required=False)

    def post(self, request, pk=None):
        user = request.user
        body = request.data
        internship = Internship.objects.filter(pk=pk).first()
        if not internship:
            return respond(404, "No Internship with this id")
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Fail", serializer.errors)
        serializer.validated_data['user'] = user
        serializer.validated_data['internship'] = internship
        internship_obj = Internship(**serializer.validated_data)
        internship_obj.save()
        return respond(200, "Success")
