from django.contrib import admin
from .models import Quiz, Question

class QuestionInline(admin.TabularInline):
	model = Question
	extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'video_url', 'owner', 'created_at', 'updated_at')
	search_fields = ('title', 'video_url', 'owner__username')
	list_filter = ('created_at', 'owner')
	inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'quiz', 'question_title', 'answer', 'created_at', 'updated_at')
	search_fields = ('question_title', 'answer', 'quiz__title')
	list_filter = ('created_at', 'quiz')
from django.contrib import admin

# Register your models here.
