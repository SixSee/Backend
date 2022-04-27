from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from Excelegal.helpers import respond
from .serializers import SubjectsSerializer
from .models import Subjects, Question, Quiz
from .serializers import QuestionSerializer


class QuestionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def list(self, request):
        user = request.user
        if not user.isAdmin():
            return respond(200, "Only for admin users")

        questions = Question.objects.all()
        serializer = self.serializer_class(questions, many=True)
        return respond(200, "Success", serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        if not user.isAdmin():
            return respond(200, "Only for admin users")
        question = Question.objects.filter(pk=pk).first()
        if not question:
            return respond(400, "No question with this id")
        serializer = self.serializer_class(question)
        return respond(200, "Success", serializer.data)

    def create(self, request):
        user = request.user
        if not user.isAdmin():
            return respond(200, "Only for admin users")
        body = request.data
        serializer = self.serializer_class(data=body)
        if serializer.is_valid():
            serializer.save()
            return respond(200, "Success")
        return respond(400, "Fail", serializer.errors)

    def update(self, request, pk=None):
        user = request.user
        if not user.isAdmin():
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
        if not user.isAdmin():
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
        max_time = serializers.TimeField(required=True)
        subjects = SubjectsSerializer(required=True)
        no_of_questions = serializers.IntegerField(required=True)

    def create(self, request):
        user = request.user
        if not user.isAdmin():
            return respond(400, "Only for admin users")

        body = request.data
        serializer = self.InputSerializer(data=body)
        if not serializer.is_valid():
            return respond(400, "Failure", serializer.errors)
        quiz = Quiz.objects.create(owner=user, **serializer.validated_data)
        
        
    # Question
    # Approve by admin

    # Quiz
    # Create a quiz
    # Update quiz
    # Delete quiz
    # List quiz
