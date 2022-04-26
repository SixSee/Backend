from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from Excelegal.helpers import respond
from .models import Subjects, Question
from .serializers import QuestionSerializer


class QuestionViewSet(ViewSet, CreateModelMixin):
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


class ListSubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subjects.objects.values('id', 'name').all()
        return respond(200, "Success", list(subjects))

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
