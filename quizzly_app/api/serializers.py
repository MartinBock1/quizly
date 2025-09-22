from rest_framework import serializers
from quizzly_app.models import Quiz, Question

class QuestionSerializer(serializers.ModelSerializer):
	"""
	Serializer for the Question model.
	Serializes question fields for API responses and input validation.
	"""
	class Meta:
		"""
		Meta configuration for QuestionSerializer.
		Specifies model and fields to include in serialization.
		"""
		model = Question
		fields = [
			'id',
			'question_title',
			'question_options',
			'answer',
			'created_at',
			'updated_at'
		]

class QuizSerializer(serializers.ModelSerializer):
	"""
	Serializer for the Quiz model.
	Includes nested questions using QuestionSerializer.
	Serializes quiz fields for API responses and input validation.
	"""
	questions = QuestionSerializer(many=True, read_only=True)

	class Meta:
		"""
		Meta configuration for QuizSerializer.
		Specifies model and fields to include in serialization.
		"""
		model = Quiz
		fields = [
			'id',
			'title',
			'description',
			'created_at',
			'updated_at',
			'video_url',
			'questions'
		]
