from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.api.decorators import allowed_users, my_classroom, ownes_exam

from exam.models import Exam, Marks
from exam.api.serializers import AddExamSerializer, StudentExamSerializer
from passlib.hash import django_pbkdf2_sha256

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# If sucessfull returns { {"id": int , "name":"exam_name", "public": bool, "deduct": bool, "date_created": date, "number_of_exercises": int}, ... } 
# If no exam is associated returns { 'v': True, 'm': 'No exams associated' }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def get_professor_exams_view(request):
    try:
        exams_data = list(Exam.objects.filter(teacher__id=request.user.id).values('id', 'name', 'public', 'deduct', 'date_created'))
        if not exams_data:
            return JsonResponse({ 'v': True, 'm': 'No exams associated' }, safe=False)
        
        for exam in exams_data:
            exam["number_of_exercises"] = Marks.objects.filter(exam__id=exam["id"]).count()

        return JsonResponse(exams_data, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)


# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# Receives a JSON with the following fields:{
#    "name": "name_of:exam",
#    "exercises" : [{"exercise": ex_id, "mark":float(mark)},
#                   {"exercise":ex_id, "mark":float(mark)}, ...],
#    "password":"pwd_to_enter_test" ,
#    "classrooms":[class_id1, class_id2, ....],
#    "public":0 
#    "deduct":0
#} 
# NOTE: OPTIONAL FIELDS: "classroom", "public"(default=True), "deduct"(default=False)
# Creates a new exam object
# If successful returns: { "v": True, "m": <int> exam.id }
# If unsuccessful returns: { "v": False, "m": Error message }
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
            exam = exam_serializer.save(exercises=exam_data["exercises"])
            return JsonResponse({ 'v': True, 'm': exam.id }, safe=False)

        return JsonResponse({ 'v': False, 'm': exam_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)


# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# Only users created the given exam can access 
# Receives exam id trough URL
# Deletes exam object 
# If successful returns: { "v": True, "m": None}
# If unsuccessful returns: { "v": False, "m": Error message }
@csrf_exempt
@api_view(["DELETE", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@ownes_exam()
def delete_exam_view(request, id):
    try:
        Exam.objects.get(id=id).delete()
        #Marks.objects.filter(exam=id).delete()     # Not needed django does this automatically
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)

    return JsonResponse({ 'v': True, 'm': None}, safe=False)


# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# Only the creator of the exam can edit the exam
# Receives exam id trough URL 
# Receives a JSON with the following model: {
#    "name": "exam1",
#    "exercises" : [{"exercise":1, "mark":10},
#                   {"exercise":2, "mark":10}, ...],
#    "password":"pass",
#    "classrooms":[],
#    "public":0
#    "deduct":0
#}
# NOTE: all the fields are optional, if keyword "exercises" is present it must follow the structure above 
# If successful returns: { "v": True, "m": None}
# If unsuccessful returns: { "v": False, "m": Error message }
@csrf_exempt
@api_view(["PATCH", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@ownes_exam()
def update_exam_view(request, id):
    try:
        exam = Exam.objects.get(id=id)
        print("exam", exam)
        exam_data = JSONParser().parse(request)
        print("exam_data", exam_data)
        exam_serializer = AddExamSerializer(instance=exam, data=exam_data, partial=True)
        
        if exam_serializer.is_valid():
            exam_serializer.update(exam, exam_serializer.validated_data, exercises= exam_data["exercises"] if "exercises" in exam_data else None)
            return JsonResponse({ 'v': True, 'm': None}, safe=False)
        
        return JsonResponse({ 'v': False, 'm': exam_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)


# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Returns id and name of the exams associated with the classroom that are public (exam.public=1)
# If sucessfull returns { {"id": int , "name":"exam_name", "teacher's_first_name": "name"}, ... } 
# If no exam is associated returns { 'v': True, 'm': 'No exams associated' }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@my_classroom()
def get_classroom_exams_view(request, id):
    try:
        exams_data = list(Exam.objects.filter(classrooms__id=id, public=True).values('id', 'name', 'teacher__first_name'))
        if not exams_data:
            return JsonResponse({ 'v': True, 'm': 'No exams associated' }, safe=False)

        return JsonResponse(exams_data, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)


# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Student (user.role==1) can access
# Receives JSON with the field "pass"
# Receives exam id trough URL
# If successful returns: { 
#   "id": exam_id,
#   "name": "exam_name",
#   "exercises": [
#        {
#            "id": 1,
#            "question": "q1",
#            "ans1": "a1",
#            "ans2": "a2",
#            "ans3": "a3",
#            "correct": "ca",
#            "unit": "V",
#            "img": null,
#            "mark": 10.0
#       },
#       { another_exercises_of_exam }, ...]
# }
# If unsuccessful returns: { "v": False, "m": Error message }
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
    
        exam_data = StudentExamSerializer(exam).data
        #adds the mark for the exercise to the serialized exercises
        for mark in Marks.objects.filter(exam=exam.id).values('exercise', 'mark'):
            for exercise in exam_data["exercises"]:
                if exercise["id"] == mark["exercise"]:
                    exercise["mark"] = float(mark["mark"])
                    break
        return JsonResponse(exam_data, safe=False)
    except TypeError as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)
