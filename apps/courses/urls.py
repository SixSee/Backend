from django.http import HttpResponse
from django.urls import path,include
from rest_framework_nested import routers

from .views import CreateCourseViewSet, CreateCourseTopicViewSet

router = routers.SimpleRouter()
router.register(r'course', CreateCourseViewSet, basename='course')
topic_router = routers.NestedSimpleRouter(router, r'course', lookup='course')
topic_router.register(r'topic', CreateCourseTopicViewSet, basename='course-topic')


# router.register(r'courses/topic', CreateCourseTopicViewSet, basename='topic')


def ping(request):
    return HttpResponse("pong")


urlpatterns = [
    path('ping', ping),
    path(r'', include(router.urls)),
    path(r'', include(topic_router.urls))
]
