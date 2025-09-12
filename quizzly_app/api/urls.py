from django.urls import path
from .views import CreateQuizView, UserQuizListView

urlpatterns = [
	path('createQuiz/', CreateQuizView.as_view(), name='create_quiz'),
	path('quizzes/', UserQuizListView.as_view(), name='user_quizzes'),
]
