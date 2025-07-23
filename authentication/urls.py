from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('send-code/', views.send_auth_code, name='send_auth_code'),
    path('verify-code/', views.verify_auth_code, name='verify_auth_code'),
    path('profile/', views.get_profile, name='get_profile'),
    path('activate-invite/', views.activate_invite_code, name='activate_invite_code'),
]
