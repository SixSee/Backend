from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from Excelegal.dao import dao_handler
from Excelegal.helpers import respond
from apps.authentication.serializers import UserSerializer
from .models import Blog, BlogReview
from .serializers import BlogsSerializer, BlogReviewSerializer


class LatestBlogView(APIView):
    def get(self, request):
        blog_type = request.GET.get('type', 'blog')
        blogs = (
            Blog.objects.filter(is_archived=False, is_live=True, type=blog_type)
                .order_by('created_at', 'updated_at', 'title')
                .all()
        )
        serializer = BlogsSerializer(blogs, many=True)
        return respond(200, "Success", serializer.data)


class BlogsViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'blog_slug'

    class OutputSerializer(serializers.ModelSerializer):
        owner = UserSerializer()
        reviews = BlogReviewSerializer(many=True)

        class Meta:
            model = Blog
            fields = ("id", "title", "image", "slug", "text", "owner", "type", "reviews")

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True, allow_null=False)
        text = serializers.CharField(required=False, allow_null=True)
        type = serializers.ChoiceField(choices=Blog.BlogTypes, required=True, allow_blank=False, allow_null=False)
        image = serializers.ImageField(required=False, allow_null=False, allow_empty_file=False)

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

    def update(self, request, blog_slug=None):
        user = request.user
        body = request.data
        blog = dao_handler.blogs_dao.get_by_slug(blog_slug)
        if not blog:
            return respond(400, "No blog with this slug")

        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(200, "Fail", serializer.errors)
        serializer.validated_data['owner'] = user
        dao_handler.blogs_dao.save_from_dict(serializer.validated_data, blog)
        return respond(200, "Success")

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

    def destroy(self, request, blog_slug=None):
        user = request.user
        blog = dao_handler.blogs_dao.get_by_slug(blog_slug)
        if not blog:
            return respond(400, "No blog with this slug")
        blog.delete()
        return respond(200, "Success")


class BlogReviewView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = BlogReview
            fields = ['id', 'review_by', 'text', 'rating', 'created_at', 'updated_at']

    class InputSerializer(serializers.Serializer):
        text = serializers.CharField(required=False, allow_blank=True)
        rating = serializers.IntegerField(required=True, min_value=0, max_value=5)

    def get(self, request, blog_slug=None, format=None):
        blog = dao_handler.blogs_dao.get_by_slug(blog_slug)
        if not blog:
            return respond(200, "No blog with this slug")

        reviews = blog.blogreview_set.all()
        serializer = self.OutputSerializer(reviews, many=True)
        return respond(200, "Success", serializer.data)

    def post(self, request, blog_slug=None):
        body = request.data
        user = request.user
        blog = dao_handler.blogs_dao.get_by_slug(blog_slug)
        if not blog:
            return respond(200, "No blog with this slug")

        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Fail", serializer.errors)

        serializer.validated_data['review_by'] = user
        serializer.validated_data['blog'] = blog
        dao_handler.blogs_review_dao.create_review(**serializer.validated_data)
        return respond(200, "Success")

    def put(self, request, blog_slug=None):
        body = request.data
        user = request.user

        blog = dao_handler.blogs_dao.get_by_slug(blog_slug)
        if not blog:
            return respond(200, "No blog with this slug")

        pk = request.GET.get('id', None)
        review: apps.blogs.models.BlogReview = dao_handler.blogs_review_dao.get_by_id(id=pk)
        if not review:
            return respond(400, "No review found with this id")

        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Fail", serializer.errors)
        if user.id != review.review_by.id:
            return respond(400, "This review doesn't belong to you")

        review.text = serializer.validated_data.get('text')
        review.rating = serializer.validated_data.get('rating')
        review.save()
        return respond(200, "Success")
