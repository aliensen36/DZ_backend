from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Referral, ReferralSettings
from loyalty_app.models import  LoyaltyCard, PointsTransaction

@receiver(post_save, sender=User)
def handle_referral_and_points(sender, instance, created, **kwargs):
    # Проверяем, что пользователь только что был создан и у него указан реферальный код
    if created and instance.referral_code_used:
        try:
            loyalty_card = instance.loyalty_card
        except LoyaltyCard.DoesNotExist:
            return
        
        referral_settings = ReferralSettings.objects.first()
        if not referral_settings:
            return
        
        # Ищем реферальную запись, которая соответствует использованному коду и еще не завершена
        referral = Referral.objects.filter(referral_code=instance.referral_code_used, invitee__isnull=True).first()

        if referral:
            inviter = referral.inviter

            # Проверяем, что награда еще не была начислена
            if referral.is_rewarded:
                return

            # Начисляем баллы пригласившему, если у него есть карта лояльности
            if inviter.loyalty_card:
                PointsTransaction.objects.create(
                    points=referral_settings.inviter_points,
                    price=0.0,
                    transaction_type='начисление',
                    card_id=inviter.loyalty_card,
                    resident_id=None
                )

            # Начисляем баллы приглашенному, если у него есть карта лояльности
            if loyalty_card:
                PointsTransaction.objects.create(
                    points=referral_settings.invitee_points,
                    price=0.0,
                    transaction_type='начисление',
                    card_id=loyalty_card,
                    resident_id=None
                )
            
            referral.invitee = instance
            referral.is_rewarded = True 
            referral.save() 