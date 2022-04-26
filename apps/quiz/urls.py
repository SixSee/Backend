from django.urls import path, include
from .views import (ListSubjectsView, QuestionViewSet)
from rest_framework import routers
router = routers.SimpleRouter()
router.register(r'question', QuestionViewSet, basename='quiz')


urlpatterns = [
    # path('question/',),
    # path('question/',),
    # path('question/',),
    # path('question/',)
    path('subjects/', ListSubjectsView.as_view()),
    path('', include(router.urls))
    ## Question
    # Add question
    # Remove question
    # Update a question
    # Approve by admin

    # Get list of courses

    # Quiz
    # Create a quiz
    # Update quiz
    # Delete quiz
    # List quiz

]
