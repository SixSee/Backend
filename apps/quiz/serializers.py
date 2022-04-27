from rest_framework import serializers

from .models import (Question, QuestionChoice, Subjects)


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ("choice", "is_correct")


class SubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ('id', 'name')


class QuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoiceSerializer(many=True)
    subjects = SubjectsSerializer(many=True)
    created_by = serializers.UUIDField(required=True)

    class Meta:
        model = Question
        fields = ("id", "name", "explanation", "is_approved", "subjects", "choices", "created_by")
        depth = 1
        read_only_fields = ['id']

    def get_created_by(self, instance):
        return instance.created_by.id if instance.created_by else None

    def create(self, validated_data:dict):
        subjects_list = []
        subjects = validated_data.pop('subjects')

        question_choices = validated_data.pop('choices')
        validated_data['created_by_id'] = str(validated_data.pop('created_by'))
        question = Question.objects.create(**validated_data)

        for subject in subjects:
            sub = Subjects.objects.get(name=subject.get('name'))
            subjects_list.append(sub)
        question.subjects.set(subjects_list)

        for choice in question_choices:
            choice_obj = QuestionChoice.objects.create(question=question,
                                                       choice=choice.get('choice'),
                                                       is_correct=choice.get('is_correct'))
        return question

    def update(self, instance: Question, validated_data):
        subjects = validated_data.pop('subjects')
        choices_data: dict = validated_data.pop('choices')
        choices = instance.choices.all()

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        subjects_list = []
        for subject in subjects:
            sub = Subjects.objects.get(name=subject.get('name'))
            subjects_list.append(sub)
        instance.subjects.set(subjects_list)

        for index in range(0, choices.count()):
            choice_obj = choices[index]
            choice_obj.choice = choices_data[index].get('choice')
            choice_obj.is_correct = choices_data[index].get('is_correct')
            choice_obj.save()

        instance.save()
        return instance
