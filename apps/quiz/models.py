import json

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User
from apps.courses.models import Course


class Question(models.Model):
    class QuestionDifficulty(models.TextChoices):
        easy = "easy", _("Easy")
        medium = "medium", _("Medium")
        hard = "hard", _("Hard")

    course = models.ManyToManyField(Course)
    name = models.TextField()
    difficulty = models.CharField(max_length=15, choices=QuestionDifficulty.choices, default=QuestionDifficulty.easy)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"for course:{self.course.id} -> {self.name[:10]}"


class QuestionChoice(models.Model):
    class Status(models.IntegerChoices):
        correct = 1
        incorrect = 0

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.TextField()
    is_correct = models.IntegerField(default=Status.incorrect, choices=Status.choices)


class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ManyToManyField(Course)
    name = models.TextField()
    participation = models.IntegerField(default=0)
    max_time = models.TimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    no_of_questions = models.IntegerField(default=0)
    question_ids = models.TextField(blank=True, null=True)

    def add_list_of_questions(self, questions: 'QuerySet[int]'):  # <QuerySet [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]>
        self.question_ids = str(list(questions))

    def add_question(self, question_id: int):
        question_ids_json: list = json.loads(self.question_ids)
        question_ids_json.append(question_id)
        self.question_ids = json.dumps(question_ids_json)

    def remove_question(self, question_id: int):
        question_ids_json: list = json.loads(self.question_ids)
        question_ids_json.remove(question_id)
        self.question_ids = json.dumps(question_ids)

    def number_of_participation(self):
        return self.userattemptedquiz_set.count()


class UserAttemptedQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_selected = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_choice_correct(self):
        return self.question.questionchoice_set.get(id=self.choice_selected).get_is_correct_display()


class UserAttemptedQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    # question_ids = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    attempted_questions = models.TextField(blank=True, null=True)

    def add_list_of_attempted_questions(self, questions: 'QuerySet[int]'):
        self.attempted_questions = json.dumps(questions)

    def add_attempt(self, question_id: int):
        attempted_question_json: list = json.loads(self.attempted_questions)
        attempted_question_json.append(question_id)
        self.attempted_questions = json.dumps(attempted_question_json)

    def remove_attempt(self, question_id):
        attempted_question_json: list = json.loads(self.attempted_questions)
        attempted_question_json.remove(question_id)
        self.attempted_questions = json.dumps(attempted_question_json)

    def no_of_attempted_questions(self):
        return len(json.loads(self.attempted_questions))