from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Level, Lesson

def level_list(request):
    levels = Level.objects.all()
    return render(request, 'lessons/level_list.html', {'levels': levels})

def lesson_list(request, level_code):
    level = get_object_or_404(Level, code=level_code)
    lessons = level.lessons.all()
    return render(request, 'lessons/lesson_list.html', {'level': level, 'lessons': lessons})

def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, 'lessons/lesson_detail.html', {'lesson': lesson})