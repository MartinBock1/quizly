from django.contrib import admin
from .models import Quiz, Question


"""
Admin configuration for Quiz and Question models.
Includes inline editing and custom field display for Django admin.
"""

class QuestionInline(admin.TabularInline):
	"""
	Inline admin for editing questions directly within a quiz.
	"""
	model = Question
	extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
	"""
	Admin configuration for the Quiz model.
	Customizes list display, search, filtering, and editable fields.
	Allows inline editing of related questions.
	"""
	list_display = ('id', 'title', 'video_url', 'owner', 'created_at', 'updated_at')
	search_fields = ('title', 'video_url', 'owner__username')
	list_filter = ('created_at', 'owner')
	inlines = [QuestionInline]
	fields = ('title', 'description', 'video_url', 'owner', 'created_at')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	"""
	Admin configuration for the Question model.
	Customizes list display, search, filtering, and editable fields.
	"""
	list_display = ('id', 'quiz', 'question_title', 'answer', 'created_at', 'updated_at')
	search_fields = ('question_title', 'answer', 'quiz__title')
	list_filter = ('created_at', 'quiz')
	fields = ('quiz', 'question_title', 'question_options', 'answer', 'created_at')
from django.contrib import admin
