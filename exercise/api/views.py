from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from account.api.decorators import allowed_users, ownes_exercise

from exercise.models import Exercise, Theme
from exercise.api.serializers import ExerciseSerializer, ThemeSerializer
from django.core.files.storage import default_storage
from exercise.api.utils import RULE_CHOICES


# Only authenticated teachers can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives a JSON with the following fields "theme", "question", "ans1", "ans2", "ans3", "correct", "unit", "resol"
# If sucessfull updates user data and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def add_exercise_view(request):
    try:
        exercise_data = JSONParser().parse(request)
        exercise_data["teacher"] = request.user.id
        exercise_serializer = ExerciseSerializer(data=exercise_data) 

        if exercise_serializer.is_valid():
            ex = exercise_serializer.save()
            return JsonResponse({ 'v': True, 'm': ex.id }, safe=False)

        return JsonResponse({ 'v': False, 'm': exercise_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

# Only authenticated teachers can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives a form-data with key "img" that can be null
# If sucessfull updates user data and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def update_exercise_img_view(request, id):
    try:
        ex = Exercise.objects.get(id=id)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)

    file = request.FILES['img']
    extension = file.name.split('.')[-1]
    file_name = "exercises/" + str(id) + "." + extension

    if default_storage.exists(file_name):
        default_storage.delete(file_name)

    file_path = default_storage.save(file_name, file)
    ex.img = file_path

    ex.save()
    return JsonResponse({ 'v': True, 'm': None}, safe=False)

# Everyone can acess this view
# Returns a list of theme objects { "id", "name" }
@csrf_exempt
@api_view(["GET", ])
@permission_classes([AllowAny])
def get_themes_view(request):
    try:
        theme = Theme.objects.all()
        theme_serializer = ThemeSerializer(theme, many=True)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

    return JsonResponse(theme_serializer.data, safe=False)

# Everyone can acess this view
# Returns a list of the possible units
@csrf_exempt
@api_view(["GET", ])
@permission_classes([AllowAny])
def get_units_view(request):
    list_units = []
    
    for unit in RULE_CHOICES:
        list_units.append(unit[0])

    return JsonResponse(list_units, safe=False)

# Everyone can acess this view
# Returns a list of exercises
@csrf_exempt
@api_view(["GET", ])
@permission_classes([AllowAny])
def get_exercises_view(request):
    try:
        exercise = Exercise.objects.all()
        exercise_serializer = ExerciseSerializer(exercise, many=True)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

    return JsonResponse(exercise_serializer.data, safe=False)

# Everyone can acess this view
# Returns a list of exercises created by the user
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def get_my_exercises_view(request):
    try:
        exercise = Exercise.objects.filter(teacher=request.user.id)
        exercise_serializer = ExerciseSerializer(exercise, many=True)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

    return JsonResponse(exercise_serializer.data, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only the user that created the exercise can acess this view, therefore it must also be a teacher
# If sucessfull updates user data and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["DELETE", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@ownes_exercise()
def delete_exercise_view(request, id):
    try:
        Exercise.objects.filter(id=id).delete()
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)

    return JsonResponse({ 'v': True, 'm': None}, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only the user that created the exercise can acess this view, therefore it must also be a teacher
# Receives a JSON with the following fields "question", "ans1", "ans2", "ans3", "correct", "unit", "resol"
# If sucessfull updates user data and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["PATCH", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@ownes_exercise()
def update_exercise_view(request, id):
    try:
        exercise = Exercise.objects.get(id=id)
        exercise.theme.clear()
        exercise_data = JSONParser().parse(request)
        exercise_serializer = ExerciseSerializer(instance=exercise, data=exercise_data, partial=True)
        
        if exercise_serializer.is_valid():
            exercise_serializer.update(exercise, exercise_serializer.validated_data)
            return JsonResponse({ 'v': True, 'm': None}, safe=False)
        
        return JsonResponse({ 'v': False, 'm': exercise_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
