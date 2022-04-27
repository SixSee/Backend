from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from Excelegal.helpers import respond
from .helpers import get_random_questions_for_quiz
from .models import Subjects, Question, Quiz
from .serializers import (QuestionSerializer, SubjectsSerializer, ListQuizSerializer, QuizSerializer)


class QuestionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def list(self, request):
        user = request.user
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(200, "Only for admin or staff users")

        if user.isStaff():
            questions = Question.objects.filter(created_by=user).all()
        else:
            questions = Question.objects.all()
        serializer = self.serializer_class(questions, many=True)
        return respond(200, "Success", serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(200, "Only for admin or staff users")

        question = Question.objects.filter(pk=pk).first()
        if not question:
            return respond(400, "No question with this id")
        serializer = self.serializer_class(question)
        return respond(200, "Success", serializer.data)

    def create(self, request):
        user = request.user
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(200, "Only for admin or staff users")

        body = request.data
        serializer = self.serializer_class(data=body)
        if serializer.is_valid():
            serializer.save()
            return respond(200, "Success")
        return respond(400, "Fail", serializer.errors)

    def update(self, request, pk=None):
        user = request.user
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(200, "Only for admin users")

        question = Question.objects.filter(pk=pk).first()
        if not question:
            return respond(400, "No question with this id")

        body = request.data
        serializer = self.serializer_class(question, data=body)
        if serializer.is_valid():
            serializer.save()
            return respond(200, "Success")
        return respond(400, "Fail", serializer.errors)

    def destroy(self, request, pk=None):
        user = request.user
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(400, "Only for admin users")

        question = Question.objects.filter(pk=pk).first()
        if not question:
            return respond(400, "No question with this id")

        question.delete()
        return respond(200, "Success")

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_question(self, request, pk=None):
        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")

        question = Question.objects.filter(pk=pk).first()
        if not question:
            return respond(400, "No question with this id")
        question.is_approved = True
        question.save()
        return respond(200, "Success")


class ListSubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subjects.objects.values('id', 'name').all()
        return respond(200, "Success", list(subjects))

    def post(self, request):
        user = request.user
        body = request.data
        if not user.isAdmin():
            return respond(400, "Only for admin users")
        if "name" not in body:
            return respond(400, "Name field required")
        Subjects.objects.create(name=body.get('name'))
        return respond(200, "Success")


class QuizViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        max_time = serializers.IntegerField(required=True)
        subjects = SubjectsSerializer(required=True, many=True)
        no_of_questions = serializers.IntegerField(required=True)

    def handle_subjects(self, quiz_obj, subjects):
        subjects_list = []
        for subject in subjects:
            sub = Subjects.objects.get(name=subject.get('name'))
            subjects_list.append(sub)
        quiz_obj.subjects.set(subjects_list)
        return quiz_obj

    def list(self, request):
        user = request.user
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(400, "Only for admin users")

        if user.isStaff():
            quiz = Quiz.objects.filter(created_by=user).all()
        quiz = Quiz.objects.all()

        serializer = ListQuizSerializer(quiz, many=True)

        return respond(200, "Success", serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(400, "Only for admin users")

        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz found with this id")

        serializer = QuizSerializer(quiz)
        return respond(200, "Success", serializer.data)

    def create(self, request):

        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")

        body = request.data
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Failure", serializer.errors)
        subjects = serializer.validated_data.pop('subjects')
        quiz = Quiz.objects.create(owner=user, **serializer.validated_data)
        quiz = self.handle_subjects(quiz, subjects)
        quiz.save()
        try:
            question_ids = get_random_questions_for_quiz(quiz)
        except Exception as e:
            quiz.delete()
            return respond(400, f"{e}. Please create a new quiz")
        quiz.add_list_of_questions(question_ids)
        quiz.save()
        return respond(200, "Success")

    def destroy(self, request, pk=None):
        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")
        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz found with this id")
        quiz.delete()
        return respond(200, "Success")

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_quiz(self, request, pk=None):
        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")

        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz with this id")
        quiz.is_approved = True
        quiz.save()
        return respond(200, "Success")

    @action(detail=True, methods=['post'], url_path='completed')
    def complete_quiz(self, request, pk=None):
        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")

        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz with this id")
        quiz.is_completed = True
        quiz.save()
        return respond(200, "Success")


class LatestQuizzesView(APIView):
    def get(self, request):
        quiz = Quiz.objects.filter(is_approved=True, is_completed=False).order_by('created_at', 'updated_at').all()
        serializer = QuizSerializer(quiz, many=True)
        return respond(200, "Success", serializer.data)


class StartQuiz(APIView):
    def get(self, request):
        user = request.user
        pass