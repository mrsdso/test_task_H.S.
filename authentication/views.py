from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.openapi import OpenApiResponse
import random
import time

from .models import User, AuthCode
from .serializers import (
    PhoneAuthSerializer, 
    CodeVerifySerializer, 
    UserProfileSerializer, 
    ActivateInviteCodeSerializer
)
from referrals.models import Referral


@extend_schema(
    tags=['Authentication'],
    summary='Отправка кода авторизации',
    description='Отправляет 4-значный код авторизации на указанный номер телефона',
    request=PhoneAuthSerializer,
    responses={
        200: OpenApiResponse(description='Код успешно отправлен'),
        400: OpenApiResponse(description='Неверные данные'),
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={'phone_number': '+71234567890'},
            request_only=True,
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_auth_code(request):
    """Отправка кода авторизации на номер телефона"""
    serializer = PhoneAuthSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        
        # Имитация задержки отправки SMS
        time.sleep(2)
        
        # Генерация 4-значного кода
        code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        # Деактивируем старые коды для этого номера
        AuthCode.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)
        
        # Сохраняем новый код
        AuthCode.objects.create(phone_number=phone_number, code=code)
        
        return Response({
            'message': f'Код отправлен на номер {phone_number}',
            'code': code  # В реальном приложении этого не должно быть!
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Проверка кода авторизации',
    description='Проверяет код авторизации и возвращает информацию о пользователе',
    request=CodeVerifySerializer,
    responses={
        200: OpenApiResponse(description='Код верен, пользователь авторизован'),
        400: OpenApiResponse(description='Неверный или истекший код'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_auth_code(request):
    """Проверка кода авторизации"""
    serializer = CodeVerifySerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        
        try:
            auth_code = AuthCode.objects.get(
                phone_number=phone_number,
                code=code,
                is_used=False
            )
            
            if auth_code.is_expired():
                return Response({
                    'error': 'Код истек'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Отмечаем код как использованный
            auth_code.is_used = True
            auth_code.save()
            
            # Получаем или создаем пользователя
            user, created = User.objects.get_or_create(phone_number=phone_number)
            
            if created:
                message = 'Новый пользователь создан'
            else:
                message = 'Пользователь найден'
            
            return Response({
                'message': message,
                'user_id': user.id,
                'is_new_user': created
            }, status=status.HTTP_200_OK)
            
        except AuthCode.DoesNotExist:
            return Response({
                'error': 'Неверный код'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Profile'],
    summary='Получение профиля пользователя',
    description='Возвращает профиль пользователя с инвайт-кодом и списком рефералов',
    responses={
        200: UserProfileSerializer,
        401: OpenApiResponse(description='Пользователь не авторизован'),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Получение профиля пользователя"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    tags=['Profile'],
    summary='Активация инвайт-кода',
    description='Активирует чужой инвайт-код для текущего пользователя',
    request=ActivateInviteCodeSerializer,
    responses={
        200: OpenApiResponse(description='Инвайт-код успешно активирован'),
        400: OpenApiResponse(description='Ошибка активации'),
        401: OpenApiResponse(description='Пользователь не авторизован'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_invite_code(request):
    """Активация инвайт-кода"""
    if request.user.activated_invite_code:
        return Response({
            'error': 'Вы уже активировали инвайт-код'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ActivateInviteCodeSerializer(data=request.data)
    if serializer.is_valid():
        invite_code = serializer.validated_data['invite_code']
        
        try:
            referrer = User.objects.get(invite_code=invite_code)
            
            if referrer == request.user:
                return Response({
                    'error': 'Нельзя активировать свой собственный инвайт-код'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Активируем инвайт-код
            request.user.activated_invite_code = invite_code
            request.user.save()
            
            # Создаем связь реферала
            Referral.objects.create(referrer=referrer, referred=request.user)
            
            return Response({
                'message': f'Инвайт-код {invite_code} успешно активирован'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Инвайт-код не найден'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
