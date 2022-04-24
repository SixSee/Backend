from rest_framework import serializers
from .models import (Question, QuestionChoice)
from Excelegal.dao import dao_handler

class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ('created_at', 'updated_at', 'difficulty')
        
    def create(self, validated_data):
        course = dao_handler.course_dao.get_by_id(validated_data.get('course', None))
        if not course:
            raise 
        question = Question()
        