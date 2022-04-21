from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from Excelegal.dao import dao_handler
from Excelegal.helpers import respond
from .models import Blog
from .serializers import BlogsSerializer


class LatestBlogView(APIView):
    def get(self, request):
        blog_type = request.GET.get('type', 'blog')
        blogs = (
            Blog.objects.filter(is_archived=False, is_live=True, type=blog_type)
            .order_by('created_at', 'updated_at')
            .all()
        )
        serializer = BlogsSerializer(blogs, many=True)
        return respond(200, "test", serializer.data)


class BlogsViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'blog_slug'

    class OutputSerializer(serializers.Serializer):
        class Meta:
            model = Blog
            exclude = ['is_live', 'is_archived', 'created_at', 'updated_at']

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True, allow_null=False)
        text = serializers.CharField(required=False, allow_null=True)
        type = serializers.ChoiceField(choices=Blog.BlogTypes, required=True, allow_blank=False, allow_null=False)

    def list(self, request):
        user = request.user
        if not user.is_anonymous and user.isAdmin():
            blogs = Blog.objects.all()
        else:
            blogs = Blog.objects.filter(is_archived=False, is_live=True).all()
        serializer = self.OutputSerializer(blogs, many=True)
        return respond(200, "Success", serializer.data)

    def retrieve(self, request, blog_slug=None):
        user = request.user
        blog = dao_handler.blogs_dao.get_by_slug(blog_slug)
        serializer = self.OutputSerializer(blog)
        return respond(200, "Success", serializer.data)

    def update(self, request, blob_slug=None):
        user = request.user
        body = request.data
        blog = dao_handler.blogs_dao.get_by_slug(blob_slug)

        if not blog:
            return respond(400, "No blog with this slug")

        if blog.owner == user or user.isAdmin():
            serializer = self.InputSerializer(data=body)
            if not serializer.is_valid():
                return respond(200, "Fail", serializer.errors)
            serializer.validated_data['owner'] = user
            serializer.validated_data['id'] = blog.id
            blog, created = dao_handler.blogs_dao.save_from_dict(serializer.validated_data)
            if created:
                print("error in update blog. Created another blog")
            return respond(200, "Success")
        else:
            return respond(400, "You dont have permission")

    def create(self, request):
        user = request.user
        body = request.data
        serializer = self.InputSerializer(data=body)

        if not serializer.is_valid():
            return respond(400, "Fail", serializer.errors)
        if user.isStudent():
            return respond(200, "You dont have permission to create course")

        serializer.validated_data['owner'] = user
        serializer.validated_data['is_archived'] = False
        serializer.validated_data['is_live'] = False
        blog = Blog(**serializer.validated_data)
        blog.save()
        return respond(200, "Success")

    def destroy(self, request, blob_slug=None):
        user = request.user
        blog = dao_handler.blogs_dao.get_by_slug(blog_slug)
        if not blog:
            return respond(400, "No blog with this slug")
        if blog.owner == user or user.isAdmin():
            blog.delete()
            return respond(200, "Success")
        else:
            return respond(400, "You dont have permission")
