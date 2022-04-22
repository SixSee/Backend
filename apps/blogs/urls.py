from django.urls import path, include
from rest_framework_nested import routers

from .views import LatestBlogView, BlogsViewSet, BlogReviewView

router = routers.SimpleRouter()
router.register(r'', BlogsViewSet, basename='blogs')

urlpatterns = [
    path('latest-blogs', LatestBlogView.as_view()),
    path('', include(router.urls)),
    path('review/<blog_slug>', BlogReviewView.as_view())

]
