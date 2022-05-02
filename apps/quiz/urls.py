from django.urls import path, include
from rest_framework import routers

from .views import (ListSubjectsView, QuestionViewSet, QuizViewSet, LatestQuizzesView, StartQuizView,
                    UserQuizQuestionsView, UserQuizAttemptView, UserCompleteQuiz, QuizIsRunningView,
                    GetListAttemptedQuizzes, RunningQuizStatus)

router = routers.SimpleRouter()
router.register(r'question', QuestionViewSet, basename='question')
router2 = routers.SimpleRouter()
router2.register(r'', QuizViewSet, basename='quiz')

urlpatterns = [
    path('subjects/', ListSubjectsView.as_view()),
    path('get-latest-quizzes/', LatestQuizzesView.as_view()),
    path('q/', include(router2.urls)),
    path('start-quiz/<pk>', StartQuizView.as_view()),
    path('start-quiz/<int:pk>/questions', UserQuizQuestionsView.as_view()),
    path('start-quiz/<int:pk>/attempt-question', UserQuizAttemptView.as_view()),
    path('start-quiz/<int:pk>/complete', UserCompleteQuiz.as_view()),
    path('start-quiz/<int:pk>/status', RunningQuizStatus.as_view()),
    path('is-running/', QuizIsRunningView.as_view()),
    path('attempted-quizzes/', GetListAttemptedQuizzes.as_view()),
    path('', include(router.urls)),
]
