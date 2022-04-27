from django.contrib import admin

from .models import Subjects, Question, QuestionChoice, Quiz, UserAttemptedQuestion, UserAttemptedQuiz


@admin.register(Subjects)
class SubjectsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'is_approved',
        'difficulty',
        'created_by',
        'explanation',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_by', 'is_approved', 'created_at', 'updated_at')
    raw_id_fields = ('courses', 'subjects')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'choice', 'is_correct')
    list_filter = ('question',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'owner',
        'name',
        'is_approved',
        'participation',
        'max_time',
        'is_completed',
        'created_at',
        'updated_at',
        'no_of_questions',
        'question_ids',
    )
    list_filter = ('owner', 'is_completed', 'created_at', 'updated_at')
    raw_id_fields = ('courses', 'subjects')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(UserAttemptedQuestion)
class UserAttemptedQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'question',
        'choice_selected',
        'created_at',
        'updated_at',
    )
    list_filter = ('question', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(UserAttemptedQuiz)
class UserAttemptedQuizAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'quiz',
        'started_at',
        'completed_at',
        'attempted_questions',
    )
    list_filter = ('user', 'quiz', 'started_at', 'completed_at')