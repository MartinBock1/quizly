from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class Quiz(models.Model):
	"""
	Model for a quiz.
	Contains title, description, creation date, update date, video URL, and owner.
	"""
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(default=timezone.now, editable=True)
	updated_at = models.DateTimeField(auto_now=True)
	video_url = models.URLField()
	owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='quizzes')

	def __str__(self):
		return self.title

class Question(models.Model):
	"""
	Model for a quiz question.
	Contains reference to quiz, question text, options, answer, creation and update date.
	"""
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
	question_title = models.CharField(max_length=255)
	question_options = models.JSONField()
	answer = models.CharField(max_length=255)
	created_at = models.DateTimeField(default=timezone.now, editable=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.question_title
from django.db import models
