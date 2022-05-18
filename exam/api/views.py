from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.api.decorators import allowed_users

from exam.models import Exam
from exam.api.serializers import AddExamSerializer, StudentExamSerializer
from passlib.hash import django_pbkdf2_sha256

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def add_exam_view(request):
    try:
        exam_data = JSONParser().parse(request)
        exam_data["teacher"] = request.user.id
        exam_serializer = AddExamSerializer(data=exam_data) 

        if exam_serializer.is_valid():
            exam = exam_serializer.save()
            return JsonResponse({ 'v': True, 'm': exam.id }, safe=False)

        return JsonResponse({ 'v': False, 'm': exam_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Student"])
#@my_classroom()
def student_exam_view(request, id):
    data = JSONParser().parse(request)
    try:
        exam = Exam.objects.get(id=id)

        # Can't use built in funtcion check_password function to check classroom password
        # this function is from passlib.hash and checks if the given secret (aka data["password"]) 
        # is correct using the django store password format <algorithm>$<iterations>$<salt>$<hash>
        # the default algorithm django uses is PBKDF2_SHA256
        # if another algorithm is used, opt for other function to verify 
        if not django_pbkdf2_sha256.verify(data["password"], exam.password):
            return JsonResponse({ 'v': False, 'm': "Incorrect Credentials" }, safe=False)
    
        exam_serializer = StudentExamSerializer(Exam.objects.get(id=id))
        return JsonResponse(exam_serializer.data, safe=False)
    except TypeError as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)
