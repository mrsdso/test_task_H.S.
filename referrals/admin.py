from django.contrib import admin
from .models import Referral


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('referrer__phone_number', 'referred__phone_number')
    ordering = ('-created_at',)
