from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import login, logout

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.shortcuts import redirect
from .tokens import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage 

from account.api.serializers import RegistrationSerialiazer
from account.models import Account
from account.api.utils import *
from django.core.files.storage import default_storage
from django.core.validators import validate_email


# Everyone can acess this view
# Receives JSON with keyswords "email", "first_name", "last_name", "birth_date", "password", "role" that can't be null
# Keyword "role" can only be 1(Student) or 2(Teacher)
# If sucessfull registration returns { "v": True, "m": None }
# If unsuccessful registration:
# Email already in use returns { "v": False, "m": "account with this email already exists" }
# Email not valid returns { "v": False, "m": "Enter a valid email address" }
# ATTENTION: Both cases above can happen at the same time
@csrf_exempt
@api_view(["POST",])
@permission_classes([AllowAny])
def registration_view(request):
    try:
        data = {}
        account_serializer = RegistrationSerialiazer(data=JSONParser().parse(request))  # Handles received data and instanciated user
        if account_serializer.is_valid():                                               # Checks if serializer is valid
            account = account_serializer.save()                                         # Saves new user
            
            data['v'] = True
            data['m'] = None
            # data["token"] = Token.objects.get_or_create(user=account)[0].key
            # data["expired"], data["token"] = token_expire_handler(data["token"])

            current_site = get_current_site(request)  

            from django.core.mail import EmailMultiAlternatives
            subject, from_email, to = 'Ativação de conta no Learning-Electronics', settings.EMAIL_HOST_USER, account.email
            text_content = 'This is an important message.'
            html_content = '''<!DOCTYPE html>
            <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
            <head>
                <meta charset="utf-8"> <!-- utf-8 works for most cases -->
                <meta name="viewport" content="width=device-width"> <!-- Forcing initial-scale shouldn't be necessary -->
                <meta http-equiv="X-UA-Compatible" content="IE=edge"> <!-- Use the latest (edge) version of IE rendering engine -->
                <meta name="x-apple-disable-message-reformatting">  <!-- Disable auto-scale in iOS 10 Mail entirely -->
                <meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no"> <!-- Tell iOS not to automatically link certain text strings. -->
                <title></title> <!-- The title tag shows in email notifications, like Android 4.4. -->

                <!-- CSS Reset : BEGIN -->
                <style>

                    /* What it does: Remove spaces around the email design added by some email clients. */
                    /* Beware: It can remove the padding / margin and add a background color to the compose a reply window. */
                    html,
                    body {
                        margin: 0 !important;
                        padding: 0 !important;
                        height: 100% !important;
                        width: 100% !important;
                    }

                    /* What it does: Stops email clients resizing small text. */
                    * {
                        -ms-text-size-adjust: 100%;
                        -webkit-text-size-adjust: 100%;
                    }

                    /* What it does: Centers email on Android 4.4 */
                    div[style*="margin: 16px 0"] {
                        margin: 0 !important;
                    }

                    /* What it does: Stops Outlook from adding extra spacing to tables. */
                    table,
                    td {
                        mso-table-lspace: 0pt !important;
                        mso-table-rspace: 0pt !important;
                    }

                    /* What it does: Fixes webkit padding issue. */
                    table {
                        border-spacing: 0 !important;
                        border-collapse: collapse !important;
                        table-layout: fixed !important;
                        margin: 0 auto !important;
                    }

                    /* What it does: Uses a better rendering method when resizing images in IE. */
                    img {
                        -ms-interpolation-mode:bicubic;
                    }

                    /* What it does: Prevents Windows 10 Mail from underlining links despite inline CSS. Styles for underlined links should be inline. */
                    a {
                        text-decoration: none;
                    }

                    /* What it does: A work-around for email clients meddling in triggered links. */
                    a[x-apple-data-detectors],  /* iOS */
                    .unstyle-auto-detected-links a,
                    .aBn {
                        border-bottom: 0 !important;
                        cursor: default !important;
                        color: inherit !important;
                        text-decoration: none !important;
                        font-size: inherit !important;
                        font-family: inherit !important;
                        font-weight: inherit !important;
                        line-height: inherit !important;
                    }

                    /* What it does: Prevents Gmail from changing the text color in conversation threads. */
                    .im {
                        color: inherit !important;
                    }

                    /* What it does: Prevents Gmail from displaying a download button on large, non-linked images. */
                    .a6S {
                        display: none !important;
                        opacity: 0.01 !important;
                    }
                    /* If the above doesn't work, add a .g-img class to any image in question. */
                    img.g-img + div {
                        display: none !important;
                    }

                    /* What it does: Removes right gutter in Gmail iOS app: https://github.com/TedGoas/Cerberus/issues/89  */
                    /* Create one of these media queries for each additional viewport size you'd like to fix */

                    /* iPhone 4, 4S, 5, 5S, 5C, and 5SE */
                    @media only screen and (min-device-width: 320px) and (max-device-width: 374px) {
                        u ~ div .email-container {
                            min-width: 320px !important;
                        }
                    }
                    /* iPhone 6, 6S, 7, 8, and X */
                    @media only screen and (min-device-width: 375px) and (max-device-width: 413px) {
                        u ~ div .email-container {
                            min-width: 375px !important;
                        }
                    }
                    /* iPhone 6+, 7+, and 8+ */
                    @media only screen and (min-device-width: 414px) {
                        u ~ div .email-container {
                            min-width: 414px !important;
                        }
                    }

                </style>

                <!-- What it does: Makes background images in 72ppi Outlook render at correct size. -->
                <!--[if gte mso 9]>
                <xml>
                    <o:OfficeDocumentSettings>
                        <o:AllowPNG/>
                        <o:PixelsPerInch>96</o:PixelsPerInch>
                    </o:OfficeDocumentSettings>
                </xml>
                <![endif]-->

                <!-- CSS Reset : END -->

                <!-- Progressive Enhancements : BEGIN -->
                <style>

                    /* What it does: Hover styles for buttons */
                    .button-td,
                    .button-a {
                        transition: all 100ms ease-in;
                    }
                    .button-td-primary:hover,
                    .button-a-primary:hover {
                        background: #555555 !important;
                        border-color: #555555 !important;
                    }

                    /* Media Queries */
                    @media screen and (max-width: 480px) {

                        /* What it does: Forces table cells into full-width rows. */
                        .stack-column,
                        .stack-column-center {
                            display: block !important;
                            width: 100% !important;
                            max-width: 100% !important;
                            direction: ltr !important;
                        }
                        /* And center justify these ones. */
                        .stack-column-center {
                            text-align: center !important;
                        }

                        /* What it does: Generic utility class for centering. Useful for images, buttons, and nested tables. */
                        .center-on-narrow {
                            text-align: center !important;
                            display: block !important;
                            margin-left: auto !important;
                            margin-right: auto !important;
                            float: none !important;
                        }
                        table.center-on-narrow {
                            display: inline-block !important;
                        }

                        /* What it does: Adjust typography on small screens to improve readability */
                        .email-container p {
                            font-size: 17px !important;
                        }
                    }

                </style>
                <!-- Progressive Enhancements : END -->

            </head>
            <!--
                The email background color (#222222) is defined in three places:
                1. body tag: for most email clients
                2. center tag: for Gmail and Inbox mobile apps and web versions of Gmail, GSuite, Inbox, Yahoo, AOL, Libero, Comcast, freenet, Mail.ru, Orange.fr
                3. mso conditional: For Windows 10 Mail
            -->
            <body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly; background-color: #222222;">
                <center style="width: 100%; background-color: #222222;">
                <!--[if mso | IE]>
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #222222;">
                <tr>
                <td>
                <![endif]-->

                    <!-- Visually Hidden Preheader Text : BEGIN -->
                    <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
                        (Optional) This text will appear in the inbox preview, but not the email body. It can be used to supplement the email subject line or even summarize the email's contents. Extended text preheaders (~490 characters) seems like a better UX for anyone using a screenreader or voice-command apps like Siri to dictate the contents of an email. If this text is not included, email clients will automatically populate it using the text (including image alt text) at the start of the email's body.
                    </div>
                    <!-- Visually Hidden Preheader Text : END -->

                    <!-- Create white space after the desired preview text so email clients don’t pull other distracting text into the inbox preview. Extend as necessary. -->
                    <!-- Preview Text Spacing Hack : BEGIN -->
                    <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
                        &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                    </div>
                    <!-- Preview Text Spacing Hack : END -->

                    <!--
                        Set the email width. Defined in two places:
                        1. max-width for all clients except Desktop Windows Outlook, allowing the email to squish on narrow but never go wider than 680px.
                        2. MSO tags for Desktop Windows Outlook enforce a 680px width.
                        Note: The Fluid and Responsive templates have a different width (600px). The hybrid grid is more "fragile", and I've found that 680px is a good width. Change with caution.
                    -->
                    <div style="max-width: 680px; margin: 0 auto;" class="email-container">
                        <!--[if mso]>
                        <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="680">
                        <tr>
                        <td>
                        <![endif]-->

                        <!-- Email Body : BEGIN -->
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: auto;">
                            <!-- Email Header : BEGIN -->
                            <tr>
                                <td style="padding: 20px 0; text-align: center">
                                    <img src="https://via.placeholder.com/200x50" width="200" height="50" alt="alt_text" border="0" style="height: auto; background: #dddddd; font-family: sans-serif; font-size: 15px; line-height: 15px; color: #555555;">
                                </td>
                            </tr>
                            <!-- Email Header : END -->

                            <!-- Hero Image, Flush : BEGIN -->
                            <tr>
                                <td style="background-color: #ffffff;">
                                    <img src="https://via.placeholder.com/1360x600" width="680" height="" alt="alt_text" border="0" style="width: 100%; max-width: 680px; height: auto; background: #dddddd; font-family: sans-serif; font-size: 15px; line-height: 15px; color: #555555; margin: auto; display: block;" class="g-img">
                                </td>
                            </tr>
                            <!-- Hero Image, Flush : END -->

                            <!-- 1 Column Text + Button : BEGIN -->
                            <tr>
                                <td style="background-color: #ffffff;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="padding: 20px; font-family: sans-serif; font-size: 15px; line-height: 20px; color: #555555;">
                                                <h1 style="margin: 0 0 10px; font-size: 25px; line-height: 30px; color: #333333; font-weight: normal;">Olá ''' + account.first_name + ''',</h1>
                                                <p style="margin: 0 0 10px;">Obrigado por te registares na nossa plataforma! Aqui poderás ...</p>
                                                <ul style="padding: 0; margin: 0; list-style-type: disc;">
                                                    <li style="margin:0 0 10px 30px;" class="list-item-first">A list item.</li>
                                                    <li style="margin:0 0 10px 30px;">Another list item here.</li>
                                                    <li style="margin: 0 0 0 30px;" class="list-item-last">Everyone gets a list item, list items for everyone!</li>
                                                </ul>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 0 20px 20px;">
                                                <!-- Button : BEGIN -->
                                                <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: auto;">
                                                    <tr>
                                                        <td class="button-td button-td-primary" style="border-radius: 4px; background: #222222;">
                                                            <a class="button-a button-a-primary" style="background: #222222; border: 1px solid #000000; font-family: sans-serif; font-size: 15px; line-height: 15px; text-decoration: none; padding: 13px 17px; color: #ffffff; display: block; border-radius: 4px;" 
                                                            href="''' + render_to_string('url.html', {    
                                                            'domain': current_site.domain,  
                                                            'uid': urlsafe_base64_encode(force_bytes(account.pk)),  
                                                            'token': account_activation_token.make_token(account),  
                                                        }) + '''">Verifica o teu E-mail</a>
                                                        </td>
                                                    </tr>
                                                </table>
                                                <!-- Button : END -->
                                            </td>
                                        </tr>

                                    </table>
                                </td>
                            </tr>
                            <!-- 1 Column Text + Button : END -->

                            <!-- 2 Even Columns : BEGIN -->
                            <tr>
                                <td align="center" valign="top" style="font-size:0; padding: 10px; background-color: #ffffff;">
                                    <!--[if mso]>
                                    <table role="presentation" border="0" cellspacing="0" cellpadding="0" width="660">
                                    <tr>
                                    <td valign="top" width="330">
                                    <![endif]-->
                                    <div style="display:inline-block; margin: 0 -1px; width:100%; min-width:200px; max-width:330px; vertical-align:top;" class="stack-column">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="padding: 10px;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="font-size: 14px; text-align: left;">
                                                        <tr>
                                                            <td>
                                                                <img src="https://via.placeholder.com/310" width="310" height="" border="0" alt="alt_text" style="width: 100%; max-width: 310px; height: auto; background: #dddddd; font-family: sans-serif; font-size: 15px; line-height: 20px; color: #555555;" class="center-on-narrow">
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td style="font-family: sans-serif; font-size: 15px; line-height: 20px; color: #555555; padding-top: 10px;" class="stack-column-center">
                                                                <p style="margin: 0;">Maecenas sed ante pellentesque, posuere leo id, eleifend dolor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                    <!--[if mso]>
                                    </td>
                                    <td valign="top" width="330">
                                    <![endif]-->
                                    <div style="display:inline-block; margin: 0 -1px; width:100%; min-width:200px; max-width:330px; vertical-align:top;" class="stack-column">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="padding: 10px;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="font-size: 14px;text-align: left;">
                                                        <tr>
                                                            <td>
                                                                <img src="https://via.placeholder.com/310" width="310" height="" border="0" alt="alt_text" style="width: 100%; max-width: 310px; height: auto; background: #dddddd; font-family: sans-serif; font-size: 15px; line-height: 20px; color: #555555;" class="center-on-narrow">
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td style="font-family: sans-serif; font-size: 15px; line-height: 20px; color: #555555; padding-top: 10px;" class="stack-column-center">
                                                                <p style="margin: 0;">Maecenas sed ante pellentesque, posuere leo id, eleifend dolor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                    <!--[if mso]>
                                    </td>
                                    </tr>
                                    </table>
                                    <![endif]-->
                                </td>
                            </tr>
                            <!-- 2 Even Columns : END -->

                            <!-- Clear Spacer : BEGIN -->
                            <tr>
                                <td aria-hidden="true" height="40" style="font-size: 0px; line-height: 0px;">
                                    &nbsp;
                                </td>
                            </tr>
                            <!-- Clear Spacer : END -->

            

                        </table>
                        <!-- Email Body : END -->

                        <!-- Email Footer : BEGIN -->
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="max-width: 680px;">
                            <tr>
                                <td style="padding: 20px; font-family: sans-serif; font-size: 12px; line-height: 15px; text-align: center; color: #888888;">
                                    <webversion style="color: #cccccc; text-decoration: underline; font-weight: bold;">View as a Web Page</webversion>
                                    <br><br>
                                    Learning-Electronics
                                </td>
                            </tr>
                        </table>
                        <!-- Email Footer : END -->

                        <!--[if mso]>
                        </td>
                        </tr>
                        </table>
                        <![endif]-->
                    </div>

                    <!-- Full Bleed Background Section : BEGIN -->
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #709f2b;">
                        <tr>
                            <td>
                                <div align="center" style="max-width: 680px; margin: auto;" class="email-container">
                                    <!--[if mso]>
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="680" align="center">
                                    <tr>
                                    <td>
                                    <![endif]-->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="padding: 20px; text-align: left; font-family: sans-serif; font-size: 15px; line-height: 20px; color: #ffffff;">
                                                <p style="margin: 0;">Maecenas sed ante pellentesque, posuere leo id, eleifend dolor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Praesent laoreet malesuada cursus. Maecenas scelerisque congue eros eu posuere. Praesent in felis ut velit pretium lobortis rhoncus ut&nbsp;erat.</p>
                                            </td>
                                        </tr>
                                    </table>
                                    <!--[if mso]>
                                    </td>
                                    </tr>
                                    </table>
                                    <![endif]-->
                                </div>
                            </td>
                        </tr>
                    </table>
                    <!-- Full Bleed Background Section : END -->

                <!--[if mso | IE]>
                </td>
                </tr>
                </table>
                <![endif]-->
                </center>
            </body>
            </html>'''

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            data['v'] = False
            data['m'] = account_serializer.errors

        return JsonResponse(data, safe=False)

    except IntegrityError as e:
            account = Account.objects.get(username='')
            account.delete()
            data['v'] = False
            data['m'] = ValidationError(str(e))
            return JsonResponse(data, safe=False)
    except KeyError as e:
            data['v'] = False
            data['m'] = ValidationError(str(e))
            return JsonResponse(data, safe=False)

# View used for user activation
# If sucessfull redirects to successeful page
# If fails redirects to error page
@csrf_exempt
@api_view(["GET",])
@permission_classes([AllowAny])
def activate(request, uidb64, token):  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        account = Account.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        account = None  
    
    if account is not None and account_activation_token.check_token(account, token):  
        account.is_active = True
        account.save()
        return redirect('http://localhost:4200/success-register')
    else:  
        account.delete()
        return redirect('http://localhost:4200/failed-register')

# Everyone can acess this view
# Receives JSON with keyswords "email", "password" that can't be null
# If sucessfull login returns: { "v":True, "m": None, "token": generated_auth_token }
# If account not found returns: { "v":False, "m": "Account not found" }
# If unsuccessful login returns: "Incorrect Credentials" 
# If account is inactive returns: "Account not active"
@csrf_exempt
@api_view(["POST",])
@permission_classes([AllowAny])
def login_view(request):
    login_data = JSONParser().parse(request)                                            # Handles received data
    try:
        account = Account.objects.get(email=login_data['email'])                        # Gets account of user with the given email
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': "Account not found" }, safe=False)

    if not account.check_password(login_data["password"]):                              # Checks if the given password is correct
        return JsonResponse({ 'v': False, 'm': "Incorrect Credentials" }, safe=False)

    if account:
        data = {}
        if account.is_active:
            login(request, account)                                                     # Logs in user
            data['v'] = True
            data['m'] = None
            data['t'] = Token.objects.get_or_create(user=account)[0].key                # Creates or gets token for that specific user
            #data["expired"], data["token"] = token_expire_handler(data["token"]) 
            return JsonResponse(data, safe=False)
        else:
            data['v'] = False
            data['m'] = "Not active"
            return JsonResponse(data, safe=False) 
    else:
        return JsonResponse({ 'v': False, 'm': 'Account not found' }, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Takes user's auth token, deletes it and logouts out user
# If sucessfull returns { "v":True, "m": None }
# If failed returns { "v":False, "m": Error message }
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()        # Deletes user's auth_token
        logout(request)                         # Logs out user

        return JsonResponse({ 'v': True, 'm': None }, safe=False)
    except Exception as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives JSON with keyswords "old_pwd", "new_pwd" that can't be null
# If sucessfull it changes user password and returns: { "v": True, "m": None, "token": generated_auth_token }
# If unsuccessful nothing happens and returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
def change_password(request):
    packet = JSONParser().parse(request)                    # Handles received data
    try:
        account = Account.objects.get(email=request.user)   # Gets account of user that sent the request (trough generated_auth_token)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)
    
    if not account.check_password(packet['old_pwd']):       # Checks if the current password is correct
        return JsonResponse({ 'v': False, 'm': "Incorrect Credentials" }, safe=False)

    if account.is_active:
        account.set_password(packet['new_pwd'])     # Sets new password as current password
        account.save()                              # Saves changes
        login(request, account)                     # Logs user again
        data = {}
        data['v'] = True
        data['m'] = None
        data['t'] = Token.objects.get_or_create(user=account)[0].key    # Creates or gets token for that specific user
        
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({ 'v': False, 'm': "Not Active" }, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives user token and gets user info
# If sucessfull returns: { "v": True, "m": None, "info": {"first_name", "last_name", "email", "birth_date", "joined", "role" }}
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET",])
@permission_classes([IsAuthenticated])
def profile_view(request):
    try:
        account = Account.objects.get(email=request.user)   # Gets account of user that sent the request (trough generated_auth_token)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)

    info = {}
    info['first_name'] = account.first_name
    info['last_name'] = account.last_name
    info['email'] = account.email
    info['birth_date'] = account.birth_date
    info['joined'] = account.date_joined
    info['role'] = "Student" if account.role==1 else "Teacher"

    try:
        info['avatar'] = account.avatar.url
    except BaseException as e:
        info['avatar'] = None

    return JsonResponse({ 'v': True, 'm': None, 'info': info }, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives JSON with keyswords "password", "email" that can't be null
# If sucessfull makes the user inactive and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST",])
@permission_classes([IsAuthenticated])   
def delete_view(request):
    packet = JSONParser().parse(request)                    # Handles received data
    try:
        account = Account.objects.get(email=request.user)   # Gets account of user that sent the request (trough generated_auth_token)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)

    if not account.check_password(packet['password']) or account.email != packet['email']:       # Checks if the current password is correct
        return JsonResponse({ 'v': False, 'm': "Incorrect Credentials" }, safe=False)

    account.is_active = False
    account.email = str(account.id) + "@deleted.com"
    account.first_name = ""
    account.last_name = ""
    account.role = 0
    account.save()
    return JsonResponse({ 'v': True, 'm': None}, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives JSON with keyswords "email", "first_name", "last_name", "birth_date" that can't be null
# If sucessfull updates user data and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST",])
@permission_classes([IsAuthenticated]) 
def update_profile(request):
    packet = JSONParser().parse(request)                    # Handles received data
    try:
        account = Account.objects.get(email=request.user)   # Gets account of user that sent the request (trough generated_auth_token)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)

    try:
        validate_email(packet['email'])
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm':{"email":str(e)}}, safe=False)
    account.email = packet['email']
    account.first_name = packet['first_name']
    account.last_name  = packet['last_name']
    account.birth_date = packet['birth_date']
    account.save()
    return JsonResponse({ 'v': True, 'm': None}, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives a form-data with key "avatar" that can't be null
# If sucessfull updates user data and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST",])
@permission_classes([IsAuthenticated]) 
def upload_avatar(request):
    try:
        account = Account.objects.get(email=request.user)   # Gets account of user that sent the request (trough generated_auth_token)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)

    file = request.FILES['avatar']
    extension = file.name.split('.')[-1]
    file_name = "users/" + str(account.id) + "." + extension

    if default_storage.exists(file_name):
        default_storage.delete(file_name)

    file_path = default_storage.save(file_name, file)
    account.avatar = file_path

    account.save()
    return JsonResponse({ 'v': True, 'm': None}, safe=False)
