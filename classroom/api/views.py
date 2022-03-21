import json
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from account.api.decorators import my_classroom, allowed_users

from classroom.models import Classroom
from classroom.api.serializers import AccountInfo, ClassroomSerializer

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Returns id and name of ALL the classrooms
# If sucessfull returns { {"id": int , "name":"classroom_name"}, ... } 
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
def get_classrooms_view(request):
    try:
        classrooms_data = list(Classroom.objects.all().values('id', 'name'))
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

    return JsonResponse(classrooms_data, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Returns id and name of all the classrooms the user is linked to
# If sucessfull returns { {"id": int , "name":"classroom_name"}, ... } 
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@my_classroom()
def get_my_classrooms_view(request):
    try:
        if request.user.role == 1:
            classrooms_data = list(request.user.student.all().values('id', 'name'))
        else:
            classrooms_data = list(request.user.teacher.all().values('id', 'name'))

        return JsonResponse(classrooms_data, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Returns detailed info of the classroom user is linked to
# If sucessfull returns {
#   "id": <int> classroom_id ,
#   "name": <string> class_name,
#   "teacher": "1 : Tiago Marques",
#   "students": [ "1 : Tiago Marques" ]
#   }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@my_classroom()
def get_info_classroom_view(request, id):
    try:
        classrooms_serializer = ClassroomSerializer(Classroom.objects.get(id=id))
        return JsonResponse(classrooms_serializer.data, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only user who have the role Teacher (user.role==2) can access
# Receives a JSON with the following fields "name" and "password"
# If successful returns: { "v": True, "m": classroom.id }
# If unsuccessful returns: { "v": False, "m": Error message }
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def add_classroom_view(request):
    try:
        classroom_data = JSONParser().parse(request)
        classroom_data["teacher"] = { "id":request.user.id , "first_name": request.user.first_name, "last_name": request.user.last_name }
        classroom_data["students"] = None
        classroom_serializer = ClassroomSerializer(data=classroom_data) 

        if classroom_serializer.is_valid():
            classroom = classroom_serializer.save()
            return JsonResponse({ 'v': True, 'm': classroom.id }, safe=False)

        return JsonResponse({ 'v': False, 'm': classroom_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only user who have the role Teacher (user.role==2) can access
# Receives classroom id trough URL 
# If successful returns: { "v": True, "m": None}
# If unsuccessful returns: { "v": False, "m": Error message }
@csrf_exempt
@api_view(["DELETE", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@my_classroom()
def delete_classroom_view(request, id):
	try:
		Classroom.objects.get(id=id).delete()
	except BaseException as e:
		return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)

	return JsonResponse({ 'v': True, 'm': None}, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Student"])
def enter_classroom_view(request, id):
	data = JSONParser().parse(request)
	try:
		classroom = Classroom.object.get(id=id)
		#how to check password?
		classroom.students.add(request.user)
		classroom.save()
	except TypeError as e:
		return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)
	except BaseException as e:
		return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)