from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import AuthCode, User
from referrals.models import Referral

User = get_user_model()


class AuthenticationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.phone = "+71234567890"
        
    def test_send_auth_code(self):
        """Тест отправки кода авторизации"""
        response = self.client.post('/api/auth/send-code/', {
            'phone_number': self.phone
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('code', response.data)
        
        # Проверяем, что код сохранился в БД
        auth_code = AuthCode.objects.filter(phone_number=self.phone).first()
        self.assertIsNotNone(auth_code)
        self.assertEqual(auth_code.code, response.data['code'])
        
    def test_verify_auth_code(self):
        """Тест проверки кода авторизации"""
        # Сначала отправляем код
        send_response = self.client.post('/api/auth/send-code/', {
            'phone_number': self.phone
        }, format='json')
        code = send_response.data['code']
        
        # Проверяем код
        verify_response = self.client.post('/api/auth/verify-code/', {
            'phone_number': self.phone,
            'code': code
        }, format='json')
        
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', verify_response.data)
        self.assertIn('is_new_user', verify_response.data)
        
        # Проверяем, что пользователь создался
        user = User.objects.filter(phone_number=self.phone).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.invite_code)  # Проверяем наличие инвайт-кода
        
    def test_get_profile(self):
        """Тест получения профиля пользователя"""
        # Создаем пользователя
        user = User.objects.create(phone_number=self.phone)
        
        # Запрашиваем профиль с header X-User-ID
        response = self.client.get('/api/auth/profile/', HTTP_X_USER_ID=str(user.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.phone)
        self.assertTrue(response.data['invite_code'])
        self.assertEqual(response.data['referrals'], [])
        
    def test_activate_invite_code(self):
        """Тест активации инвайт-кода"""
        # Создаем двух пользователей
        user1 = User.objects.create(phone_number="+71111111111")
        user2 = User.objects.create(phone_number="+72222222222")
        
        # user2 активирует инвайт-код user1
        response = self.client.post('/api/auth/activate-invite/', {
            'invite_code': user1.invite_code
        }, HTTP_X_USER_ID=str(user2.id), format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что код активировался
        user2.refresh_from_db()
        self.assertEqual(user2.activated_invite_code, user1.invite_code)
        
        # Проверяем создание реферальной связи
        referral = Referral.objects.filter(referrer=user1, referred=user2).first()
        self.assertIsNotNone(referral)
        
    def test_activate_own_invite_code(self):
        """Тест невозможности активации собственного инвайт-кода"""
        user = User.objects.create(phone_number=self.phone)
        
        response = self.client.post('/api/auth/activate-invite/', {
            'invite_code': user.invite_code
        }, HTTP_X_USER_ID=str(user.id), format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_activate_invite_code_twice(self):
        """Тест невозможности активации двух инвайт-кодов"""
        user1 = User.objects.create(phone_number="+71111111111")
        user2 = User.objects.create(phone_number="+72222222222")
        user3 = User.objects.create(phone_number="+73333333333")
        
        # user3 активирует инвайт-код user1
        self.client.post('/api/auth/activate-invite/', {
            'invite_code': user1.invite_code
        }, HTTP_X_USER_ID=str(user3.id), format='json')
        
        # user3 пытается активировать инвайт-код user2
        response = self.client.post('/api/auth/activate-invite/', {
            'invite_code': user2.invite_code
        }, HTTP_X_USER_ID=str(user3.id), format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
