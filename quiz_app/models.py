from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    """
    Quiz Model - stores quiz information and metadata
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    youtube_url = models.URLField()
    transcript = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} - {self.user.username}'


class Question(models.Model):
    """
    Question Model - stores individual quiz questions
    """
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order']
    
    def __str__(self):
        return f'{self.quiz.title} - Q{self.order}'


class Answer(models.Model):
    """
    Answer Model - stores possible answers for questions
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['order']
    
    def __str__(self):
        return self.answer_text[:50]
