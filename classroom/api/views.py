from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from account.api.decorators import my_classroom, ownes_exercise, allowed_users

from classroom.models import Classroom
from classroom.api.serializers import ClassroomSerializer

@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
def get_classes_view(request):
    try:
        classroom = Classroom.objects.all()
        classroom_serializer = ClassroomSerializer(classroom, many=True)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

    return JsonResponse(classroom_serializer.data, safe=False)

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def add_classroom_view(request):
    try:
        classroom_data = JSONParser().parse(request)
        classroom_data["teacher"] = request.user.id
        classroom_serializer = ClassroomSerializer(data=classroom_data) 

        if classroom_serializer.is_valid():
            classroom = classroom_serializer.save()
            return JsonResponse({ 'v': True, 'm': classroom.id }, safe=False)

        return JsonResponse({ 'v': False, 'm': classroom_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)