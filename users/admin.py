from django.contrib import admin
from .models import UserProfile, CoinTransaction, Sticker, StickerPurchase


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'coins', 'avatar', 'created_at']
    search_fields = ['user__username']


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'amount', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['profile__user__username', 'reason']


@admin.register(Sticker)
class StickerAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'name', 'price', 'order']
    list_editable = ['price', 'order']


@admin.register(StickerPurchase)
class StickerPurchaseAdmin(admin.ModelAdmin):
    list_display = ['profile', 'sticker', 'purchased_at']
    list_filter = ['purchased_at']
