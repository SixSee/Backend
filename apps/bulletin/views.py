from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from Excelegal.dao import dao_handler
from Excelegal.helpers import respond
from .models import Bulletin


class BulletinView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True)
        description = serializers.CharField(required=True)
        category = serializers.CharField(required=True)
        action_title = serializers.CharField(required=True)
        action_link = serializers.URLField(required=True)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Bulletin
            fields = ('title', 'slug', 'owner',
                      'description', 'action_title', 'action_link',
                      'visible', 'category', 'created_at', 'updated_at')

    def get(self, request):
        user = request.user
        if user.is_anonymous or user.isStudent():
            bulletin = Bulletin.objects.filter(visible=True).order_by('-created_at').all()
        elif user.isAdmin():
            bulletin = Bulletin.objects.order_by('-created_at').all()
        elif user.isStaff():
            bulletin = Bulletin.objects.filter(owner=user).order_by('-created_at').all()
        serializer = self.OutputSerializer(bulletin)
        return respond(200, "Success", serializer.data)

    def post(self, request):
        user = request.user
        body = request.data
        if user.role < user.STAFF:
            return respond(400, "Only for Admin and Staff")
        serializer = self.InputSerializer(body)
        if not serializer.is_valid():
            return respond(400, "Failure", serializer.errors)
        bull_obj = Bulletin.objects.create(owner=user, **serializer.validated_data)
        return respond(200, "Success")

    def put(self, request):
        user = request.user
        body: dict = request.data

        slug = body.pop('slug')
        bulletin = Bulletin.objects.filter(slug=slug).first()
        if not bulletin:
            return respond(400, "No bulletin with this id")

        if user.role < user.STAFF:
            return respond(400, "Only for Admin and Staff")

        serializer = self.InputSerializer(body)
        if not serializer.is_valid():
            return respond(400, "Failure", serializer.errors)

        dao_handler.bulletin_dao.save_from_dict(serializer.validated_data, bulletin)
        return respond(200, "Success")

    def destroy(self, request):
        user = request.user
        slug = body.pop('slug')

        bulletin = Bulletin.objects.filter(slug=slug).first()
        if not bulletin:
            return respond(400, "No bulletin with this id")

        if bulletin.owner.id == user.id or user.isAdmin():
            bulletin.delete()
            return respond(200, "Success")

        return respond(400, "Not your bulletin")