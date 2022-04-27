from django.urls import path, include
from .views import (ListSubjectsView, QuestionViewSet, QuizViewSet, LatestQuizzesView)
from rest_framework import routers
router = routers.SimpleRouter()
router.register(r'question', QuestionViewSet, basename='question')
router2 = routers.SimpleRouter()
router2.register(r'', QuizViewSet, basename='quiz')

urlpatterns = [
    path('subjects/', ListSubjectsView.as_view()),
    path('get-latest-quizzes/', LatestQuizzesView.as_view()),
    path('', include(router.urls)),
    path('q/', include(router2.urls))
    
    # Get list of courses

    # Quiz
    # Create a quiz
    # Update quiz
    # Delete quiz
    # List quiz

]
