import json
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from lessons.models import Level
from .models import Word, WordProgress

# Har bir so'zni birinchi marta to'g'ri bilganda beriladigan coin
COINS_PER_WORD = 5

MODES = {
    'all':    {'title': "To'liq mashq (5 bosqich)", 'icon': '🔥', 'desc': "Barcha bosqich ketma-ket"},
    'study':  {'title': "So'zlarni o'rganish",        'icon': '🃏', 'desc': "Kartochkalar"},
    'en_uz':  {'title': "Inglizcha → O'zbekcha",       'icon': '🇬🇧', 'desc': "O'zbekchasini tanlang"},
    'uz_en':  {'title': "O'zbekcha → Inglizcha",       'icon': '🇺🇿', 'desc': "Inglizchasini tanlang"},
    'write':  {'title': "Yozish",                       'icon': '✍️', 'desc': "Inglizchasini yozing"},
    'listen': {'title': "Tinglab gapirish",            'icon': '🎤', 'desc': "Ovoz bilan takrorlang"},
}



def vocab_home(request):
    levels = Level.objects.all()
    level_data = []
    for level in levels:
        count = level.words.count()
        if count:
            level_data.append({'level': level, 'count': count})
    return render(request, 'vocabulary/vocab_home.html', {
        'level_data': level_data,
        'modes': MODES,
    })


def _words_for_level(level_code):
    if level_code == 'all':
        return list(Word.objects.all())
    level = get_object_or_404(Level, code=level_code)
    return list(level.words.all())

@login_required
def practice(request, level_code, mode):
    if mode not in MODES:
        return redirect('vocab_home')

    words = _words_for_level(level_code)
    random.shuffle(words)
    limit = 8 if mode == 'all' else 20
    words = words[:limit]

    all_uz = list(set(w.uzbek for w in Word.objects.all()))
    all_en = list(set(w.english for w in Word.objects.all()))

    cards = []
    for w in words:
        item = {'id': w.id, 'english': w.english, 'uzbek': w.uzbek,
                'example': w.example, 'emoji': w.emoji}
        d_uz = random.sample([u for u in all_uz if u != w.uzbek], k=min(3, max(0, len(all_uz) - 1)))
        opts_uz = d_uz + [w.uzbek]
        random.shuffle(opts_uz)
        item['opts_en_uz'] = opts_uz
        d_en = random.sample([e for e in all_en if e != w.english], k=min(3, max(0, len(all_en) - 1)))
        opts_en = d_en + [w.english]
        random.shuffle(opts_en)
        item['opts_uz_en'] = opts_en
        cards.append(item)

    return render(request, 'vocabulary/practice.html', {
        'mode': mode, 'mode_info': MODES[mode], 'level_code': level_code,
        'cards_json': json.dumps(cards), 'coins_per_word': COINS_PER_WORD,
    })



@login_required
def check_word(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    data = json.loads(request.body)
    word_id = data.get('word_id')
    correct = data.get('correct', False)

    word = get_object_or_404(Word, pk=word_id)
    progress, _ = WordProgress.objects.get_or_create(user=request.user, word=word)

    awarded = 0
    if correct:
        progress.correct_count += 1
        progress.learned = True
        if not progress.coins_awarded:
            request.user.profile.add_coins(COINS_PER_WORD, f"So'z yodlandi: {word.english}")
            progress.coins_awarded = True
            awarded = COINS_PER_WORD
    progress.save()

    return JsonResponse({'ok': True, 'awarded': awarded, 'coins': request.user.profile.coins})

@login_required
def not_learned(request):
    progress = WordProgress.objects.filter(
        user=request.user, coins_awarded=False
    ).select_related('word')
    words = [p.word for p in progress]
    return render(request, 'vocabulary/not_learned.html', {'words': words})
