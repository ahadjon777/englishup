from django.contrib import admin
from .models import Level, Lesson, LessonCompletion


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'order']
    ordering = ['order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'video_coin_reward', 'order']
    list_filter = ['level']
    ordering = ['level', 'order']


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'video_watched', 'coins_awarded', 'completed_at']
    list_filter = ['video_watched', 'coins_awarded']
