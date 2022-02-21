from datetime import timedelta
from django.utils import timezone
from django.conf import settings

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import authentication

# If token is expired, it will be removed and a new one will be created
def token_expire_handler(token):
    is_expired = is_token_expired(token)
    if is_expired:
        token.delete()
        token = Token.objects.create(user = token.user)
    return is_expired, token

# Check if token is expired or not
def is_token_expired(token):
    return expires_in(token) < timedelta(seconds = 0)

# Returns time left for token
def expires_in(token):
    time_elapsed = timezone.now() - token.created()
    left_time = timedelta(seconds = settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
    return left_time

# CUSTOMIZED DEFAULT_AUTHENTICATION_CLASS
class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            raise AuthenticationFailed("User Not Active")

        is_expired, token = token_expire_handler(token)
        if is_expired:
            raise AuthenticationFailed("The Token is expired")
        
        return (token.user, token)

# Changes Token Authentication keyword from "Token" to "Bearer"
class TokenAuthentication(authentication.TokenAuthentication):
    authentication.TokenAuthentication.keyword = 'Bearer'