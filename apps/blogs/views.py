from django.shortcuts import render

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from Excelegal.helpers import respond
from rest_framework.views import APIView
from .models import Blog
from Excelegal.dao import dao_handler
from .serializers import BlogsSerializer


class LatestBlogView(APIView):
    def get(self, request):
        blog_type = request.GET.get('type', 'blog')
        blogs = dao_handler.blogs_dao.get_by_type(blog_type=blog_type)
        serializer = BlogsSerializer(blogs)
        return respond(200, "test", serializer.data)
