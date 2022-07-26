from django.urls import path, include
from rest_framework_nested import routers
from .views import (InternshipViewSet, LatestInternships, ApplyInternshipView)

router = routers.SimpleRouter()
router.register(r'', InternshipViewSet, basename='')

urlpatterns = [
    path('latest-internship', LatestInternships.as_view()),
    path('apply/<int:pk>', ApplyInternshipView.as_view()),
    path('', include(router.urls)),
]
