from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()


class SimpleAuthMiddleware(MiddlewareMixin):
    """
    Простая аутентификация по user_id в заголовке для тестирования API
    В продакшене следует использовать токены или сессии
    """
    
    def process_request(self, request):
        user_id = request.META.get('HTTP_X_USER_ID')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                request.user = user
            except (User.DoesNotExist, ValueError):
                pass
        
        return None
