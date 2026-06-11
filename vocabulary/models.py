from django.db import models
from django.contrib.auth.models import User
from lessons.models import Level, Lesson


class Word(models.Model):
    english = models.CharField(max_length=100)
    uzbek = models.CharField(max_length=100)
    example = models.CharField(max_length=300, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='words', null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name='words', null=True, blank=True)
    emoji = models.CharField(max_length=10, blank=True, default='📘')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['english']

    def __str__(self):
        return f"{self.english} - {self.uzbek}"


class WordProgress(models.Model):
    """Foydalanuvchi o'rgangan so'zlar. Coin faqat birinchi yodlaganda beriladi."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_progress')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='progress')
    learned = models.BooleanField(default=False)
    correct_count = models.IntegerField(default=0)
    coins_awarded = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'word')

    def __str__(self):
        return f"{self.user.username} - {self.word.english}"
