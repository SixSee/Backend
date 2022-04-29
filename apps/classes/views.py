from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from Excelegal.helpers import respond
from .models import ScheduleClass
from rest_framework import serializers


class ScheduleClassView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField()
        meeting_id = serializers.CharField()
        meeting_at = serializers.DateTimeField()
        duration = serializers.IntegerField()

    def get(self, request):
        user = request.user
        return respond(200, "Success")

    def post(self, request):
        user = request.user
        body = request.data
        if user.isStudent():
            return respond(400, "Dont have permissions")
        return respond(200, "Success")

    def put(self, respect):
        user = request.user
        body = request.data
        return respond(200, "Success")

    def destroy(self, request):
        user = request.user
        return respond(200, "Success")
