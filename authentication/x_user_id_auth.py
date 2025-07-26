from rest_framework.authentication import BaseAuthentication
from authentication.models import User

class XUserIDAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return None
        try:
            user = User.objects.get(id=user_id)
            return (user, None)
        except User.DoesNotExist:
            return None
