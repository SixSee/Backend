from django.urls import path
from .views import LatestBlogView
urlpatterns = [
    path('latest-blogs', LatestBlogView.as_view()),
]