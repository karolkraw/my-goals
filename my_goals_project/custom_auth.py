from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
import logging

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token or not token.startswith('Bearer '):
            return None
        
        token = token[7:]  # Remove 'Bearer ' prefix
        
        try:
            # Decode the token using Spring Boot's secret key
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            
            # Extract user_id (or other claims)
            #user_id = payload.get('user_id')
            username = payload.get('username')

            """ if not user_id:
                raise AuthenticationFailed('User ID not found in token') """

            # Create a simple user object
            user = type('User', (), {'username': username, 'is_authenticated': True})()  # Add 'is_authenticated': True
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')