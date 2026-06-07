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


def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    watched = False
    if request.user.is_authenticated:
        watched = LessonCompletion.objects.filter(
            user=request.user, lesson=lesson, video_watched=True
        ).exists()
    return render(request, 'lessons/lesson_detail.html', {
        'lesson': lesson,
        'watched': watched,
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
