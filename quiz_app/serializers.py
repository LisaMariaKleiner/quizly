from rest_framework import serializers
from .models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'answer_text', 'is_correct', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'order', 'answers')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'youtube_url', 'created_at', 'updated_at', 'questions')
        read_only_fields = ('user', 'created_at', 'updated_at')
