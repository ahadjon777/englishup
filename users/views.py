from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import json
from groq import Groq

from .models import UserProfile, Sticker, StickerPurchase


# ---------------------------------------------------------------------------
# Coin helper — boshqa applar shuni chaqiradi
# ---------------------------------------------------------------------------
def award_coins(user, amount, reason=''):
    """Foydalanuvchiga coin beradi. Anonim bo'lsa hech narsa qilmaydi."""
    if not user.is_authenticated:
        return 0
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.add_coins(amount, reason)


# ---------------------------------------------------------------------------
# Bosh sahifa
# ---------------------------------------------------------------------------
def home_view(request):
    return render(request, 'home.html')


# ---------------------------------------------------------------------------
# Autentifikatsiya
# ---------------------------------------------------------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            messages.error(request, 'Username va parol kiritilishi shart.')
        elif password != password2:
            messages.error(request, 'Parollar mos kelmadi.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Bu username band.')
        else:
            user = User.objects.create_user(username=username, password=password)
            # ro'yxatdan o'tganlarga xush kelibsiz bonusi
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.add_coins(50, 'Xush kelibsiz bonusi 🎁')
            login(request, user)
            return redirect('home')

    return render(request, 'users/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Username yoki parol noto‘g‘ri.')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    transactions = profile.transactions.all()[:15]
    owned = profile.sticker_purchases.select_related('sticker').all()
    return render(request, 'users/profile.html', {
        'profile': profile,
        'transactions': transactions,
        'owned': owned,
    })


# ---------------------------------------------------------------------------
# Marketplace
# ---------------------------------------------------------------------------
def market_view(request):
    stickers = Sticker.objects.all()
    owned_ids = set()
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        owned_ids = set(profile.sticker_purchases.values_list('sticker_id', flat=True))
    return render(request, 'users/market.html', {
        'stickers': stickers,
        'owned_ids': owned_ids,
    })


@login_required
def buy_sticker(request, pk):
    from django.shortcuts import get_object_or_404
    sticker = get_object_or_404(Sticker, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if StickerPurchase.objects.filter(profile=profile, sticker=sticker).exists():
        messages.info(request, 'Bu stiker sizda allaqachon bor.')
    elif profile.spend_coins(sticker.price, f"Stiker sotib olindi: {sticker.name}"):
        StickerPurchase.objects.create(profile=profile, sticker=sticker)
        messages.success(request, f"{sticker.emoji} {sticker.name} sotib olindi!")
    else:
        messages.error(request, "Coin yetarli emas! Dars o'qing va quiz yeching. 🪙")
    return redirect('market')


# ---------------------------------------------------------------------------
# AI Tutor chatbot
# ---------------------------------------------------------------------------
client = Groq(api_key=settings.GROQ_API_KEY)


@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an English language tutor. Help users learn English. If user writes incorrect English, first correct it with explanation, then answer."
                    },
                    {"role": "user", "content": user_message}
                ]
            )

            response = completion.choices[0].message.content
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'response': f'Error: {str(e)}'})

    return render(request, 'users/chatbot.html')


# ---------------------------------------------------------------------------
# AI Battle — o'quvchi vs AI (vocabulary / grammar)
# ---------------------------------------------------------------------------
COINS_PER_BATTLE = 3  # har bir to'g'ri javob uchun


@login_required
def battle(request):
    return render(request, 'users/battle.html')


@csrf_exempt
@login_required
def battle_new(request):
    """AI bitta yangi savol yaratadi (vocabulary yoki grammar)."""
    try:
        data = json.loads(request.body)
        category = data.get('category', 'grammar')
        if category == 'vocabulary':
            topic = ("one English vocabulary question for a learner: ask the meaning of a word, "
                     "or which word fits a sentence, or a synonym/antonym")
        else:
            topic = ("one English grammar question for a learner: fill in the blank or choose the correct form, "
                     "covering tenses, articles, prepositions or similar")

        prompt = (
            f"Generate {topic}. Keep it short (max 2 sentences). "
            "Do NOT include the answer. Return ONLY JSON: {\"question\": \"...\"}"
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You create short English practice questions. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        data = json.loads(completion.choices[0].message.content)
        return JsonResponse({'ok': True, 'question': data.get('question', '')})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@csrf_exempt
@login_required
def battle_check(request):
    """AI o'quvchi javobini baholaydi va to'g'ri bo'lsa coin beradi."""
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        answer = data.get('answer', '')

        prompt = (
            f"Question: {question}\nStudent's answer: {answer}\n"
            "Decide if the student's answer is correct for this English question. "
            "Return ONLY JSON: {\"correct\": true or false, "
            "\"correct_answer\": \"the correct answer\", "
            "\"feedback\": \"one short friendly sentence of feedback\"}"
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an English teacher grading answers. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        result = json.loads(completion.choices[0].message.content)
        correct = bool(result.get('correct'))

        awarded = 0
        if correct:
            request.user.profile.add_coins(COINS_PER_BATTLE, "AI Battle: to'g'ri javob")
            awarded = COINS_PER_BATTLE

        return JsonResponse({
            'ok': True,
            'correct': correct,
            'correct_answer': result.get('correct_answer', ''),
            'feedback': result.get('feedback', ''),
            'awarded': awarded,
            'coins': request.user.profile.coins,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
