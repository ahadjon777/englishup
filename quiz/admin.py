from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'lesson', 'coin_reward', 'question_count', 'order']
    list_filter = ['level']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'order']
    list_filter = ['quiz']
    inlines = [ChoiceInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total', 'coins_awarded', 'completed_at']
    list_filter = ['quiz', 'completed_at']
