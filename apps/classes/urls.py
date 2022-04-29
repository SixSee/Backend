from django.urls import path, include

from .views import (ScheduleClassView)

urlpatterns = [
    path('', ScheduleClassView.as_view()),
]