from rest_framework import serializers

from .models import (Question, QuestionChoice)


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ("choice", "is_correct")


class QuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ("id", "name", "explanation", "is_approved", "subjects", "choices")
        # depth = 1
        read_only_fields = ['id']

    def create(self, validated_data):
        subjects = validated_data.pop('subjects')
        question_choices = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        for subject in subjects:
            question.subjects.add(subject)

        for choice in question_choices:
            choice_obj = QuestionChoice.objects.create(question=question,
                                                       choice=choice.get('choice'),
                                                       is_correct=choice.get('is_correct'))
        return question

    def update(self, instance: Question, validated_data):
        subjects_data = validated_data.pop('subjects')

        subjects = instance.subjects
        choices_data = validated_data.pop('choices')
        choices = instance.choices

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.subjects = subjects_data
        instance.save()
