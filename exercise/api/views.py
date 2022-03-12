from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from account.api.decorators import allowed_users

from exercise.models import Exercise
from exercise.api.serializers import ExerciseSerializer
from django.core.files.storage import default_storage


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
            exercise_serializer.save()        
            return JsonResponse({ 'v': True, 'm': None }, safe=False)

        return JsonResponse({ 'v': False, 'm': "Not Valid" }, safe=False)
    except Exception as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)


# Only authenticated teachers can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives a form-data with key "img" that can be null
# If sucessfull updates user data and returns: { "v": True, "m": None }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def update_exercise_img_view(request):
    try:
        ex = Exercise.objects.latest(teacher=request.user.id)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': ValidationError(str(e)) }, safe=False)

    file = request.FILES['img']
    extension = file.name.split('.')[-1]
    file_name = "exercises/" + str(ex.id) + "." + extension

    if default_storage.exists(file_name):
        default_storage.delete(file_name)

    file_path = default_storage.save(file_name, file)
    ex.img = file_path

    ex.save()
    return JsonResponse({ 'v': True, 'm': None}, safe=False)
