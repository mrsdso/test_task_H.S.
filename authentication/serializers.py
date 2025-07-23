from rest_framework import serializers
from .models import User, AuthCode


class PhoneAuthSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        # Простая валидация номера телефона
        if not value.startswith('+'):
            raise serializers.ValidationError("Номер телефона должен начинаться с +")
        return value


class CodeVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)


class UserProfileSerializer(serializers.ModelSerializer):
    referrals = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['phone_number', 'invite_code', 'activated_invite_code', 'referrals']
        read_only_fields = ['phone_number', 'invite_code']
    
    def get_referrals(self, obj):
        """Получаем список пользователей, которые использовали инвайт-код этого пользователя"""
        referrals = obj.referrals.all()
        return [referral.referred.phone_number for referral in referrals]


class ActivateInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)
    
    def validate_invite_code(self, value):
        if not User.objects.filter(invite_code=value).exists():
            raise serializers.ValidationError("Инвайт-код не существует")
        return value
