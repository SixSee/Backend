from django.urls import path, include
from rest_framework_nested import routers

from .views import (CourseViewSet, CourseTopicViewSet, CourseReviewView, LatestCoursesView)

router = routers.SimpleRouter()
router.register(r'course', CourseViewSet, basename='course')
topic_router = routers.NestedSimpleRouter(router, r'course', lookup='course')
topic_router.register(r'topic', CourseTopicViewSet, basename='course-topic')

urlpatterns = [
    path('course/latest-course/', LatestCoursesView.as_view()),
    path(r'', include(router.urls)),
    path(r'', include(topic_router.urls)),
    path('course/review/<course_slug>', CourseReviewView.as_view()),
]
