from django.http import HttpResponse
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CreateCourseViewSet

router = DefaultRouter()
router.register('',CreateCourseViewSet,basename='course')

def ping(request):
    return HttpResponse("pong")

urlpatterns = [
    path('ping', ping),

]
urlpatterns += router.urls
