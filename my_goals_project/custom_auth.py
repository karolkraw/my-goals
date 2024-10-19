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
            user_id = payload.get('user_id')

            if not user_id:
                raise AuthenticationFailed('User ID not found in token')

            # Create a simple user object
            user = type('User', (), {'id': user_id, 'is_authenticated': True})()  # Add 'is_authenticated': True
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

""" def jwt_decode_handler(token):
    try:  
        payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        logger.warning(f"Decoded token: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        raise

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            logger.warning("No authorization token found")
            return None
        
        if token.startswith('Bearer '):
            token = token[7:]  # Remove 'Bearer ' prefix
        else:
            logger.warning("Invalid authorization header format")
            return None
        
        try:
            decoded_token = jwt_decode_handler(token)
            # Here you would typically set the user object on the request
            # request.user = User.objects.get(id=decoded_token['user_id'])
            # request.auth = decoded_token
            return super().authenticate(request)
        except Exception as e:
            logger.warning(f"JWT decode error: {str(e)}")
            return None """