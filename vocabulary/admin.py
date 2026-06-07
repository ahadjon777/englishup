from django.contrib import admin
from .models import Word, WordProgress


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['english', 'uzbek', 'level', 'emoji']
    list_filter = ['level']
    search_fields = ['english', 'uzbek']


@admin.register(WordProgress)
class WordProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'learned', 'correct_count', 'coins_awarded']
    list_filter = ['learned', 'coins_awarded']
