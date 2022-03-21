from django.contrib.auth.tokens import PasswordResetTokenGenerator  
from django.utils import six

class TokenGenerator(PasswordResetTokenGenerator):  
    def _make_hash_value(self, user, timestamp):  
        return ( six.text_type(user.pk) + six.text_type(timestamp) +  six.text_type(user.is_active) )

class DeactivationTokenGenerator(PasswordResetTokenGenerator):  
    def _make_hash_value(self, user, timestamp):  
        return ( six.text_type(timestamp) + six.text_type(user.pk) + six.text_type(user.is_active) )

class ResetTokenGenerator(PasswordResetTokenGenerator):  
    def _make_hash_value(self, user, timestamp):  
        return ( six.text_type(user.is_active) + six.text_type(user.pk) + six.text_type(timestamp) )


account_activation_token = TokenGenerator()  
account_deactivation_token = DeactivationTokenGenerator() 
reset_password_token = ResetTokenGenerator()

# future use maybe
# import random
# import string
# ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)) 