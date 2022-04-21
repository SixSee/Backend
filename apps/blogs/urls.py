from django.urls import path, include
from rest_framework_nested import routers

from .views import LatestBlogView, BlogsViewSet

router = routers.SimpleRouter()
router.register(r'', BlogsViewSet, basename='blogs')

urlpatterns = [
    path('latest-blogs', LatestBlogView.as_view()),
    path('', include(router.urls)),

]
