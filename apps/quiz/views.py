from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from Excelegal.helpers import respond
from apps.authentication.serializers import UserSerializer
from .helpers import get_random_questions_for_quiz
from .models import Subjects, Question, Quiz, UserAttemptedQuiz, UserAttemptedQuestion
from .serializers import (QuestionSerializer, SubjectsSerializer, ListQuizSerializer, QuizSerializer,
                          QuestionChoiceSerializer_wo_correct, UserAttemptedQuestionSerializer)


class QuestionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
    page_size = 15

    def list(self, request):
        user = request.user
        page_number = int(request.GET.get('page_number', 1))
        limit = self.page_size
        offset = (page_number - 1) * self.page_size

        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(200, "Only for admin or staff users")

        if user.isStaff():
            questions = Question.objects.filter(created_by=user).all()[offset:offset + limit]
        else:
            questions = Question.objects.all()[offset:offset + limit]
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
            question = serializer.save()
            serializer = self.serializer_class(question)
            return respond(200, "Success", serializer.data)
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
        question.is_approved = not question.is_approved
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
    page_size = 15

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        max_time = serializers.IntegerField(required=True)
        subjects = SubjectsSerializer(required=True, many=True)
        no_of_questions = serializers.IntegerField(required=True)

    def handle_subjects(self, quiz_obj, subjects):
        subjects_list = []
        for subject in subjects:
            sub = Subjects.objects.get(name__startswith=subject.get('name'))
            subjects_list.append(sub)
        quiz_obj.subjects.set(subjects_list)
        return quiz_obj

    def list(self, request):
        user = request.user
        page_number = int(request.GET.get('page_number', 1))
        limit = self.page_size
        offset = (page_number - 1) * self.page_size
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(400, "Only for admin users")

        quiz = Quiz.objects.all()[offset:offset + limit]
        if user.isStaff():
            quiz = Quiz.objects.filter(owner=user).all()[offset:offset + limit]

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
        if not (user.is_superuser or (user.role >= user.STAFF)):
            return respond(400, "Only for admin or staff users")

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
        quiz.is_approved = not quiz.is_approved
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        attempted = request.GET.get('unattempted', 0)
        if not user.is_anonymous and attempted:
            user_quizzes = UserAttemptedQuiz.objects.filter(user=user, completed_at__isnull=False).values_list(
                'quiz_id').all()
            user_quizzes = [i[0] for i in list(user_quizzes)]
            quiz = (Quiz.objects
                    .filter(is_approved=True, is_completed=False)
                    .order_by('created_at', 'updated_at')
                    .exclude(id__in=user_quizzes).all())
        else:
            quiz = Quiz.objects.filter(is_approved=True, is_completed=False).order_by('created_at', 'updated_at').all()
        serializer = QuizSerializer(quiz, many=True)
        return respond(200, "Success", serializer.data)


class StartQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        user = request.user
        body = request.data

        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz found with this id")

        if UserAttemptedQuiz.objects.filter(user=user, quiz=quiz).exists():
            return respond(200, "Quiz already started continue to questions")

        user_quiz = UserAttemptedQuiz.objects.create(user=user,
                                                     quiz=quiz,
                                                     started_at=timezone.now())
        return respond(201, "Success")


class UserQuizQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        choices = QuestionChoiceSerializer_wo_correct(many=True)
        created_by = serializers.UUIDField()

        class Meta:
            model = Question
            fields = ("id", "name", "choices", "created_by")
            depth = 1

    def get(self, request, pk=None):
        user = request.user
        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz found with this id")
        user_quiz = UserAttemptedQuiz.objects.filter(user=user, quiz=quiz)
        if not user_quiz.exists():
            return respond(400, "Start Quiz before viewing all questions")
        user_quiz = user_quiz.first()
        quiz_question_ids = user_quiz.quiz.get_list_of_questions()
        quiz_question_objs = [Question.objects.filter(pk=pk).first() for pk in quiz_question_ids]
        serializer = self.OutputSerializer(quiz_question_objs, many=True)
        return respond(200, "Success", serializer.data)


class UserQuizAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    def can_attempt_quiz(self, started_at, max_time):
        current_time = timezone.now()
        return current_time <= (started_at + timedelta(minutes=max_time))

    def post(self, request, pk=None):
        user = request.user
        body: dict = request.data
        current_time = timezone.now()
        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz found with this id")
        max_time_minutes = quiz.max_time
        user_quiz = quiz.userattemptedquiz_set.filter(user=user).first()
        if not user_quiz:
            return respond(400, "Quiz not started")

        if not self.can_attempt_quiz(user_quiz.started_at, max_time_minutes):
            return respond(400, "Time is up")

        if ("question_id" not in body.keys()) and ("choice_selected_id" not in body.keys()):
            return respond(400, "Need question_id and choice_selected_id. Wrong body format")

        question_id = int(body.get('question_id'))
        choice_selected_id = int(body.get('choice_selected_id'))
        attempt_already = (UserAttemptedQuestion.objects
                           .filter(user_quiz=user_quiz,
                                   question_id=question_id)
                           .first())
        question_ids = quiz.get_list_of_questions()

        if question_id in question_ids:
            question = Question.objects.get(pk=question_id)
            question_choice = question.choices.get(pk=choice_selected_id)
            if attempt_already:
                attempt_already.choice_selected = question_choice.id
                attempt_already.save()
                return respond(200, "Attempt Updated")

            user_q_attempt = UserAttemptedQuestion.objects.create(
                question=question,
                choice_selected=question_choice.id,
                user_quiz_id=user_quiz.id
            )
            user_quiz.add_attempt(user_q_attempt.id)
            user_quiz.save()
            return respond(200, "Attempt Recorded")
        else:
            return respond(400, "TMKC")


class UserCompleteQuiz(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        no_of_attempted_questions = serializers.SerializerMethodField()
        user = UserSerializer()
        attempts = serializers.SerializerMethodField()
        user_quiz_id = serializers.SerializerMethodField()

        class Meta:
            model = UserAttemptedQuiz
            fields = ("user_quiz_id", "user", "started_at",
                      "completed_at", "no_of_attempted_questions",
                      "attempts")

        def get_user_quiz_id(self, instance):
            return instance.id

        def get_no_of_attempted_questions(self, instance):
            return instance.no_of_attempted_questions()

        def get_attempts(self, instance):
            attempted_question_ids = instance.get_list_of_attempted_questions()
            attempted_question_objs = [UserAttemptedQuestion.objects.get(pk=pk)
                                       for pk in attempted_question_ids]
            serializer = UserAttemptedQuestionSerializer(attempted_question_objs, many=True)
            return serializer.data

    def post(self, request, pk=None):
        user = request.user

        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz found with this id")

        user_quiz = quiz.userattemptedquiz_set.filter(user=user).first()
        if not user_quiz:
            return respond(400, "Quiz not started")
        user_quiz.completed_at = timezone.now()
        user_quiz.save()
        serializer = self.OutputSerializer(user_quiz)
        return respond(200, "Success", serializer.data)


class QuizIsRunningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_quiz = UserAttemptedQuiz.objects.filter(user=user, completed_at__isnull=True).first()
        if user_quiz:
            return respond(400, "Quiz Already Runnning... Complete running quiz ")
        return respond(200, "Success")


class RunningQuizStatus(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        no_of_attempted_questions = serializers.SerializerMethodField()
        user = UserSerializer()
        attempts = serializers.SerializerMethodField()
        user_quiz_id = serializers.SerializerMethodField()

        class Meta:
            model = UserAttemptedQuiz
            fields = ("user_quiz_id", "user", "started_at",
                      "completed_at", "no_of_attempted_questions",
                      "attempts")

        def get_user_quiz_id(self, instance):
            return instance.id

        def get_no_of_attempted_questions(self, instance):
            return instance.no_of_attempted_questions()

        def get_attempts(self, instance):
            attempted_question_ids = instance.get_list_of_attempted_questions()
            attempted_question_objs = [UserAttemptedQuestion.objects.get(pk=pk)
                                       for pk in attempted_question_ids]
            serializer = UserAttemptedQuestionSerializer(attempted_question_objs, many=True)
            return serializer.data

    def get(self, request, pk=None):
        user = request.user
        quiz = Quiz.objects.filter(pk=pk).first()
        if not quiz:
            return respond(400, "No quiz found with this id")

        user_quiz = quiz.userattemptedquiz_set.filter(user=user, quiz=quiz).first()
        if not user_quiz:
            return respond(400, "Quiz not started")
        if not UserAttemptedQuiz.objects.filter(quiz=quiz, user=user, completed_at=None).exists():
            return respond(400, "Quiz is completed")

        serializer = self.OutputSerializer(user_quiz)
        return respond(200, "Success", serializer.data)


class GetListAttemptedQuizzes(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        no_of_attempted_questions = serializers.SerializerMethodField()
        user = UserSerializer()
        attempts = serializers.SerializerMethodField()
        user_quiz_id = serializers.SerializerMethodField()
        quiz_id = serializers.SerializerMethodField()
        quiz_name = serializers.SerializerMethodField()

        class Meta:
            model = UserAttemptedQuiz
            fields = ("user_quiz_id", "user", "started_at",
                      "completed_at", "no_of_attempted_questions",
                      "attempts", 'quiz_id', 'quiz_name')

        def get_quiz_id(self, instance):
            return instance.quiz.id

        def get_quiz_name(self, instance):
            return instance.quiz.name

        def get_user_quiz_id(self, instance):
            return instance.id

        def get_no_of_attempted_questions(self, instance):
            return instance.no_of_attempted_questions()

        def get_attempts(self, instance):
            attempted_question_ids = instance.get_list_of_attempted_questions()
            attempted_question_objs = [UserAttemptedQuestion.objects.get(pk=pk)
                                       for pk in attempted_question_ids]
            serializer = UserAttemptedQuestionSerializer(attempted_question_objs, many=True)
            return serializer.data

    def get(self, request):
        user = request.user
        user_quizzes = UserAttemptedQuiz.objects.filter(user=user, completed_at__isnull=False).all()
        serializer = self.OutputSerializer(user_quizzes, many=True)
        return respond(200, "Success", serializer.data)
