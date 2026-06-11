from django.db import models
from django.contrib.auth.models import User
from lessons.models import Level, Lesson


class Quiz(models.Model):
    CATEGORY_CHOICES = [
        ('Grammar', 'Grammar'),
        ('Reading', 'Reading'),
        ('Writing', 'Writing'),
        ('Listening', 'Listening'),
        ('Vocabulary', 'Vocabulary'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Grammar')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name='quizzes', null=True, blank=True)
    coin_reward = models.IntegerField(default=20, help_text="Quizni birinchi marta yechganda beriladigan coin")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title}: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} {'✓' if self.is_correct else ''}"


class QuizAttempt(models.Model):
    """Foydalanuvchining quizni yechishi. Coin faqat birinchi marta beriladi."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    coins_awarded = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}/{self.total})"

    def percentage(self):
        return round((self.score / self.total) * 100) if self.total else 0
