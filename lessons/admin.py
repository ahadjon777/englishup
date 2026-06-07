from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Level, Lesson

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'order']
    ordering = ['order']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'order']
    list_filter = ['level']
    ordering = ['level', 'order']