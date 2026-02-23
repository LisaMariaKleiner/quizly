from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('quizzes/', views.QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:quiz_id>/', views.QuizDetailView.as_view(), name='quiz-detail'),
]
