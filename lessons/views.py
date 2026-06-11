import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Level, Lesson, LessonCompletion


def level_list(request):
    levels = Level.objects.all()
    return render(request, 'lessons/level_list.html', {'levels': levels})


def _lesson_completed(user, lesson):
    """Dars tugaganmi: shu darsning barcha homework testlari yechilgan."""
    from quiz.models import QuizAttempt
    quizzes = list(lesson.quizzes.all())
    if not quizzes:
        return True  # homework bo'lmasa, ochiq hisoblanadi
    attempted = set(QuizAttempt.objects.filter(
        user=user, quiz__in=quizzes).values_list('quiz_id', flat=True))
    return all(q.id in attempted for q in quizzes)


def _lesson_unlocked(user, lesson):
    """Dars ochiqmi: admin -> doim ochiq; aks holda oldingi dars tugagan bo'lsa."""
    if user.is_authenticated and user.is_staff:
        return True
    prev = Lesson.objects.filter(level=lesson.level, order__lt=lesson.order).order_by('-order').first()
    if prev is None:
        return True  # birinchi dars doim ochiq
    if not user.is_authenticated:
        return False
    return _lesson_completed(user, prev)


def lesson_list(request, level_code):
    level = get_object_or_404(Level, code=level_code)
    lessons = list(level.lessons.all())
    is_admin = request.user.is_authenticated and request.user.is_staff

    lesson_data = []
    prev_done = True  # birinchi dars uchun
    for lesson in lessons:
        unlocked = is_admin or prev_done
        done = False
        if request.user.is_authenticated:
            done = _lesson_completed(request.user, lesson)
        lesson_data.append({'lesson': lesson, 'unlocked': unlocked, 'done': done})
        # keyingi dars uchun: shu dars tugaganmi?
        prev_done = done if request.user.is_authenticated else False

    return render(request, 'lessons/lesson_list.html', {
        'level': level, 'lesson_data': lesson_data, 'is_admin': is_admin,
    })


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
    # Ketma-ketlik: oldingi dars tugamasa, bloklanadi (admin bundan mustasno)
    if not _lesson_unlocked(request.user, lesson):
        messages.warning(request, "🔒 Avval oldingi darsning homeworkini tugating!")
        return redirect('lesson_list', level_code=lesson.level.code)

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
