from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.api.decorators import my_classroom, allowed_users

from classroom.models import Classroom
from classroom.api.serializers import AddClassroomSerializer, ClassroomSerializer
from passlib.hash import django_pbkdf2_sha256

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
def get_my_classrooms_view(request):
    try:
        if request.user.role == 1:
            classrooms_data = list(request.user.students.all().values('id', 'name'))
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
#   "teacher": <string> "teacher_id : "teacher__first_name teacher__last_name",
#   "students": <List<String>> [ "1 : Tiago Marques" ]
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
        classroom_data["teacher"] = request.user.id
        classroom_serializer = AddClassroomSerializer(data=classroom_data) 

        if classroom_serializer.is_valid():
            classroom = classroom_serializer.create(classroom_serializer.validated_data)
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
        classroom = Classroom.objects.get(id=id)

        if not django_pbkdf2_sha256.verify(data["password"], classroom.password):
            return JsonResponse({ 'v': False, 'm': "Incorrect Credentials" }, safe=False)
    
        classroom.students.add(request.user)
        classroom.save_no_pass()
        return JsonResponse({ 'v': True, 'm': None}, safe=False)

    except TypeError as e:
        return JsonResponse({ 'v': 2, 'm': str(e)}, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': 3, 'm': str(e)}, safe=False)

@csrf_exempt
@api_view(["PATCH", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@my_classroom()
def update_classroom_view(request, id):
    try:
        classroom = Classroom.objects.get(id=id)
        classroom.students.clear()
        classroom_data = JSONParser().parse(request)
        classroom_serializer = AddClassroomSerializer(instance=classroom, data=classroom_data, partial=True)
        
        if classroom_serializer.is_valid():
            classroom_serializer.update(classroom, classroom_serializer.validated_data)
            return JsonResponse({ 'v': True, 'm': None}, safe=False)
        
        return JsonResponse({ 'v': False, 'm': classroom_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)