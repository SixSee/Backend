from django.urls import path

from .views import GetLinks

urlpatterns = [
    path('', GetLinks.as_view()),
]
