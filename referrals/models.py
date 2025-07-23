from django.db import models
from django.conf import settings


class Referral(models.Model):
    """Модель для отслеживания реферальных связей"""
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='referrals'
    )
    referred = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='referrer_info'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referrals'
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
    
    def __str__(self):
        return f"{self.referrer.phone_number} -> {self.referred.phone_number}"
