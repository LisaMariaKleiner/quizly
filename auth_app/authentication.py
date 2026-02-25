from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads tokens from cookies instead of Authorization header
    """
    
    def authenticate(self, request):
        """
        Authenticate by reading JWT token from cookies
        """
        # Try to get token from Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            # Use default behavior if Authorization header is present
            return super().authenticate(request)
        
        # Try to get token from cookies
        access_token = request.COOKIES.get('access_token')
        
        if not access_token:
            return None
        
        # Validate and return the token
        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except AuthenticationFailed:
            raise AuthenticationFailed('Access token is invalid or expired.')
