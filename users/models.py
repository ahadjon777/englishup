from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    coins = models.IntegerField(default=0)
    avatar = models.CharField(max_length=10, default='🧑‍🎓')
    bio = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.coins} coins)"

    def add_coins(self, amount, reason=''):
        """Foydalanuvchiga coin qo'shadi va tranzaksiyani yozadi."""
        self.coins += amount
        self.save()
        CoinTransaction.objects.create(
            profile=self,
            amount=amount,
            reason=reason,
        )
        return self.coins

    def spend_coins(self, amount, reason=''):
        """Coin sarflaydi. Yetarli bo'lsa True, aks holda False qaytaradi."""
        if self.coins < amount:
            return False
        self.coins -= amount
        self.save()
        CoinTransaction.objects.create(
            profile=self,
            amount=-amount,
            reason=reason,
        )
        return True


class CoinTransaction(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()  # musbat = topildi, manfiy = sarflandi
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.amount >= 0 else ''
        return f"{self.profile.user.username}: {sign}{self.amount} ({self.reason})"


# User yaratilganda avtomatik profil ochiladi
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()



class Sticker(models.Model):
    name = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10, default='🌟')
    description = models.CharField(max_length=200, blank=True)
    price = models.IntegerField(default=100, help_text="Narxi (coin)")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.emoji} {self.name} ({self.price} coin)"


class StickerPurchase(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sticker_purchases')
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE, related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'sticker')
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.profile.user.username} -> {self.sticker.name}"
