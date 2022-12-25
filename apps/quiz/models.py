import json

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User
from apps.courses.models import Course


class Subjects(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Question(models.Model):
    class QuestionDifficulty(models.TextChoices):
        easy = "easy", _("Easy")
        medium = "medium", _("Medium")
        hard = "hard", _("Hard")

    courses = models.ManyToManyField(Course, blank=True)
    subjects = models.ManyToManyField(Subjects, blank=False)
    name = models.TextField()
    difficulty = models.CharField(max_length=15, choices=QuestionDifficulty.choices, default=QuestionDifficulty.easy)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    explanation = models.TextField(default='', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name[:100]}"


class QuestionChoice(models.Model):
    class Status(models.IntegerChoices):
        correct = 1
        incorrect = 0

    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    choice = models.TextField()
    is_correct = models.IntegerField(default=Status.incorrect, choices=Status.choices)

    class Meta:
        ordering = ['pk']


class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True)
    subjects = models.ManyToManyField(Subjects)
    name = models.TextField()
    participation = models.IntegerField(default=0)
    max_time = models.IntegerField(verbose_name='Time limit in minutes')
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    no_of_questions = models.IntegerField(default=0)
    question_ids = models.TextField(default='[]')

    def add_list_of_questions(self, questions: 'list[int]'):  # <QuerySet [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]>
        self.question_ids = str(list(questions))

    def get_list_of_questions(self):
        return json.loads(self.question_ids)

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


class UserAttemptedQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)
    attempted_questions = models.TextField(default='[]')

    def add_list_of_attempted_questions(self, questions: 'QuerySet[int]'):
        self.attempted_questions = json.dumps(questions)

    def get_list_of_attempted_questions(self):
        return json.loads(self.attempted_questions)

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


class UserAttemptedQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_selected = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_quiz = models.ForeignKey(UserAttemptedQuiz, on_delete=models.CASCADE, default=None)

    def is_choice_correct(self):
        return self.question.choices.get(id=self.choice_selected).get_is_correct_display()
