from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import login, logout

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from account.api.serializers import RegistrationSerialiazer
from account.models import Account
from account.api.utils import *

# Only works with POST method
# Everyone can acess this view
# Receives JSON with keyswords "email", "username", "first_name", "last_name", "birth_date", "password" that noone can be null
# If sucessfull registration returns True
# If unsuccessful registration:
# Email already in use returns {"email" : ["account with this email already exists"]} 
# Username already in use returns {"username" : ["account with this username already exists"]} 
# ATTENTION: Both cases above can happen at the same time
@csrf_exempt
@api_view(["POST",])
@permission_classes([AllowAny])
def registration_view(request):
    try:
        data={}
        account_serializer = RegistrationSerialiazer(data=JSONParser().parse(request))  # Handles received data and instanciated user
        if account_serializer.is_valid():                                               # Checks if serializer is valid
            account = account_serializer.save()                                         # Saves new user
            data['v']=True
            data['m']=None
            """ data["token"] = Token.objects.get_or_create(user=account)[0].key
            data["expired"], data["token"] = token_expire_handler(data["token"]) """ 
        else:
            data['v']=False
            data['m']= account_serializer.errors

        return JsonResponse(data, safe=False)

    except IntegrityError as e:
            account=Account.objects.get(username='')
            account.delete()
            data['v']= False
            data['m']= ValidationError(str(e))
            return JsonResponse(False, safe=False)
    except KeyError as e:
            data['v']= False
            data['m']= ValidationError(str(e))
            return JsonResponse(False, safe=False)

# Only works with GET method
# Everyone can acess this view
# Receives JSON with keyswords "email", "password" that noone can be null
# If sucessfull login returns: { "message":True, "email": given email, "token": generated_auth_token }
# If unsuccessful login returns: "Incorrect Credentials" 
# If account is inactive returns: "Account not active"
@csrf_exempt
@api_view(["POST",])
@permission_classes([AllowAny])
def login_view(request):
    login_data = JSONParser().parse(request)                        # Handles received data
    try:
        account = Account.objects.get(email=login_data['email'])    # Gets account of user with the given email
    except BaseException as e:
        return JsonResponse({'v':False,'m':"Doesnt exist"},safe=False)

    if not account.check_password(login_data["password"]):          # Checks if the given password is correct
        return JsonResponse({'v':False,'m':"Incorrect Credentials"},safe=False)

    if account:
        data={}
        if account.is_active:
            login(request, account)                                 # Logs in user
            data['v'] = True
            data['m'] = None
            data['t'] = Token.objects.get_or_create(user=account)[0].key    # Creates or gets token for that specific user
            #data["expired"], data["token"] = token_expire_handler(data["token"]) 
            return JsonResponse(data, safe=False)
        else:
            data['v'] = False
            data['m'] = "Not active"
            return JsonResponse(data, safe=False) 

    else:
        data['v'] = False
        data['m'] = "Doesnt exist"
        return JsonResponse(data, safe=False)

# Only works with GET method
# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Takes user's auth token, deletes it and logouts out user
# Returns: True
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()        # Deletes user's auth_token
    logout(request)                         # Logs out user

    return JsonResponse({'v':True, 'm':None}, safe=False)

# Only works with GET method
# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives JSON with keyswords "old_pwd", "new_pwd" that noone can be null
# If sucessfull it changes user password and returns: { "message":True, "email": user's_email, "token": generated_auth_token }
# If unsuccessful nothing happens and returns: "Incorrect Credentials" 
# If account is inactive returns: "Account not active" 
@csrf_exempt
@api_view(["PUT", ])
@permission_classes([IsAuthenticated])
def change_password(request):

    packet = JSONParser().parse(request)                    # Handles received data
    try:
        account = Account.objects.get(email=request.user)   # Gets account of user that sent the request (trough generated_auth_token)
    except BaseException as e:
        return JsonResponse({'v':False,'m':ValidationError(str(e))},safe=False)
    
    if not account.check_password(packet['old_pwd']):       # Checks if the current password is correct
        return JsonResponse({'v':False, 'm':"Incorrect Credentials"}, safe=False)

    if account.is_active:
        account.set_password(packet['new_pwd'])     # Sets new password as current password
        account.save()                              # Saves changes
        login(request,account)                      # Logs user again
        data={}
        data['v'] = True
        data['m'] = None
        data['t'] = Token.objects.get_or_create(user=account)[0].key    # Creates or gets token for that specific user
        
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'v':False,'m':"Not Active"},safe=False)

    