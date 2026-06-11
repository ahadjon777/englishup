from django.db import models
from django.contrib.auth.models import User

class Level(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'Beginner A1'),
        ('A2', 'Elementary A2'),
        ('B1', 'Pre-Intermediate B1'),
        ('B2', 'Intermediate B2'),
        ('C1', 'Upper-Intermediate C1'),
        ('C2', 'Advanced C2'),
    ]
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, default='📚')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Lesson(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    grammar_explanation = models.TextField(blank=True)
    examples = models.TextField(blank=True)
    youtube_url = models.CharField(max_length=200, blank=True)
    video_coin_reward = models.IntegerField(default=15, help_text="Videoni birinchi marta ko'rganda beriladigan coin")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.level.code} - {self.title}"
    
    def youtube_embed_url(self):
        if self.youtube_url:
            if 'watch?v=' in self.youtube_url:
                video_id = self.youtube_url.split('watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in self.youtube_url:
                video_id = self.youtube_url.split('youtu.be/')[1]
            else:
                return self.youtube_url
            return f"https://www.youtube.com/embed/{video_id}"
        return None



class LessonCompletion(models.Model):
    """Foydalanuvchi video darslikni ko'rgani. Coin faqat birinchi marta."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_completions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completions')
    video_watched = models.BooleanField(default=False)
    coins_awarded = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
