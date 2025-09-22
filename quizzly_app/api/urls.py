from django.urls import path
from .views import CreateQuizView, UserQuizListView, UserQuizDetailView

urlpatterns = [
	path('createQuiz/', CreateQuizView.as_view(), name='create_quiz'),
	path('quizzes/', UserQuizListView.as_view(), name='user_quizzes'),
	path('quizzes/<int:id>/', UserQuizDetailView.as_view(), name='user_quiz_detail'),
]
