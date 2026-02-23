from rest_framework import serializers
from .models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'answer_text', 'is_correct', 'order')


class QuestionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for questions with all answer options
    """
    question_title = serializers.CharField(source='question_text', read_only=True)
    question_options = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ('id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at')
    
    def get_question_options(self, obj):
        """Returns all answer options"""
        return [answer.answer_text for answer in obj.answers.all().order_by('order')]
    
    def get_answer(self, obj):
        """Returns the correct answer"""
        correct_answer = obj.answers.filter(is_correct=True).first()
        return correct_answer.answer_text if correct_answer else None


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'order', 'answers', 'created_at', 'updated_at')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionDetailSerializer(many=True, read_only=True)
    video_url = serializers.CharField(source='youtube_url', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'video_url', 'created_at', 'updated_at', 'questions')
        read_only_fields = ('user', 'created_at', 'updated_at', 'video_url')


class QuizUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating quiz fields (title, description)
    """
    class Meta:
        model = Quiz
        fields = ('title', 'description')
    
    def validate_title(self, value):
        """Validate title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value


class QuizCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new quiz from a YouTube URL
    """
    url = serializers.URLField(required=True)
    
    def validate_url(self, value):
        """Validate that the URL is a YouTube URL"""
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError("Please provide a valid YouTube URL.")
        return value
