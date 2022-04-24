from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

class QuestionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self):
        user = request.user
        body = request.body

