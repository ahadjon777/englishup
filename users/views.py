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
