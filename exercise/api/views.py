from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError

from exercise.models import Exercise
from exercise.api.serializers import ExerciseSerializer

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
def add_exercise_view(request):
    try:
        exercise_data = JSONParser().parse(request)
        exercise_data["teacher"] = request.user.id
        exercise_serializer = ExerciseSerializer(data=exercise_data)
        print(exercise_serializer)
        if exercise_serializer.is_valid():
            exercise_serializer.save()
            return JsonResponse({ 'v': True, 'm': None }, safe=False)

        return JsonResponse({ 'v': False, 'm': "Not Valid" }, safe=False)
    except Exception as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
