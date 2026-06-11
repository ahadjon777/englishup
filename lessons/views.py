import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Level, Lesson, LessonCompletion


def level_list(request):
    levels = Level.objects.all()
    return render(request, 'lessons/level_list.html', {'levels': levels})


def lesson_list(request, level_code):
    level = get_object_or_404(Level, code=level_code)
    lessons = level.lessons.all()
    return render(request, 'lessons/lesson_list.html', {'level': level, 'lessons': lessons})


def level_hub(request, level_code):
    """Englify uslubidagi daraja hub'i: Vocabulary / Video / Homework."""
    level = get_object_or_404(Level, code=level_code)
    total_lessons = level.lessons.count()
    vocab_pct = video_pct = homework_pct = 0

    if request.user.is_authenticated:
        watched = LessonCompletion.objects.filter(
            user=request.user, lesson__level=level, video_watched=True).count()
        video_pct = round(watched / total_lessons * 100) if total_lessons else 0

        from vocabulary.models import Word, WordProgress
        total_words = Word.objects.filter(level=level).count()
        learned = WordProgress.objects.filter(
            user=request.user, coins_awarded=True, word__level=level).count()
        vocab_pct = round(learned / total_words * 100) if total_words else 0

        from quiz.models import Quiz, QuizAttempt
        pcts = []
        for q in Quiz.objects.filter(level=level):
            best = 0
            for a in QuizAttempt.objects.filter(user=request.user, quiz=q):
                best = max(best, a.percentage())
            pcts.append(best)
        homework_pct = round(sum(pcts) / len(pcts)) if pcts else 0

    return render(request, 'lessons/level_hub.html', {
        'level': level, 'vocab_pct': vocab_pct,
        'video_pct': video_pct, 'homework_pct': homework_pct,
    })


def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    watched = False
    if request.user.is_authenticated:
        watched = LessonCompletion.objects.filter(
            user=request.user, lesson=lesson, video_watched=True
        ).exists()
    # Shu darsga tegishli homework (testlar) va vocabulary (so'zlar)
    homework = lesson.quizzes.all().order_by('order')
    vocab_words = lesson.words.all()
    return render(request, 'lessons/lesson_detail.html', {
        'lesson': lesson,
        'watched': watched,
        'homework': homework,
        'vocab_count': vocab_words.count(),
    })


@login_required
def mark_video_watched(request, pk):
    """AJAX: video ko'rildi -> birinchi marta bo'lsa coin beradi."""
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    lesson = get_object_or_404(Lesson, pk=pk)
    completion, _ = LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)

    awarded = 0
    completion.video_watched = True
    if not completion.coins_awarded:
        request.user.profile.add_coins(lesson.video_coin_reward, f"Video ko'rildi: {lesson.title}")
        completion.coins_awarded = True
        awarded = lesson.video_coin_reward
    completion.save()

    return JsonResponse({'ok': True, 'awarded': awarded, 'coins': request.user.profile.coins})
