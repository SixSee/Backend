from django.http import HttpResponse
from django.urls import path, include
from rest_framework_nested import routers

from .views import CourseViewSet, CourseTopicViewSet

router = routers.SimpleRouter()
router.register(r'course', CourseViewSet, basename='course')
topic_router = routers.NestedSimpleRouter(router, r'course', lookup='course')
topic_router.register(r'topic', CourseTopicViewSet, basename='course-topic')


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(topic_router.urls))
]
