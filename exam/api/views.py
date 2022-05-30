from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError
from classroom.models import Classroom

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.api.decorators import allowed_users, my_classroom, ownes_exam, my_classroom_exam

from account.models import Account
from exam.models import Exam, Marks, SubmittedExam
from exam.api.serializers import AddExamSerializer, StudentExamSerializer, ProfessorExamSerializer, AddSubmittedExamSerializer
from passlib.hash import django_pbkdf2_sha256

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# If sucessfull returns { {"id": int , "name":"exam_name", "public": bool, "deduct": decimal(4, 2), "date_created": date, "number_of_exercises": int, "timer": string, "repeat":bool, "exercises":[exercise_id, exercise_id,...]}, ... } 
# If no exam is associated returns { 'v': True, 'm': 'No exams associated' }
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def get_professor_exams_view(request):
    try:
        exams_data = list(Exam.objects.filter(teacher__id=request.user.id).values('id', 'name', 'public', 'deduct', 'date_created', 'timer'))
        for exam_data in exams_data:
            exam_data["exercises"] = list(Marks.objects.filter(exam=exam_data["id"]).values('exercise__id'))
            
        if not exams_data:
            return JsonResponse({ 'v': True, 'm': 'No exams associated' }, safe=False)
        
        for exam in exams_data:
            exam["number_of_exercises"] = Marks.objects.filter(exam__id=exam["id"]).count()

        return JsonResponse(exams_data, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# If sucessfull returns: {
#    "name": "exam47",
#    "public": bool,
#    "deduct": decimal(4,2),
#    "date_created": "2022-05-25",
#    "exercises": [
#        {
#            "id": 1,
#            "question": "q1",
#            "ans1": "a1",
#            "ans2": "a2",
#            "ans3": "a3",
#            "correct": "ca",
#            "unit": "V",
#            "img": null,
#            "mark": 7.0
#        },
#        ...],
#    "timer": "02:00"(string),
#    "repeat": bool
#    "classrooms": [
#        {
#            "classroom_id": "classroom_name"
#        }, 
#        ...]
#}  
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@ownes_exam()
def get_professor_exam_info_view(request, id):
    try:
        exam = Exam.objects.get(id=id)
        exam_data = ProfessorExamSerializer(exam).data
        exam_data["classrooms"] = [ {classroom.id : classroom.name} for classroom in exam.classrooms.all()]
        #adds the mark for the exercise to the serialized exercises
        for mark in Marks.objects.filter(exam=exam.id).values('exercise', 'mark'):
            for exercise in exam_data["exercises"]:
                if exercise["id"] == mark["exercise"]:
                    exercise["mark"] = float(mark["mark"])
                    break
        return JsonResponse(exam_data, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# Receives a JSON with the following fields:{
#    "name": "name_of:exam",
#    "exercises" : [{"exercise": ex_id, "mark":float(mark)},    NOTE: mark value between 0 and 20
#                   {"exercise":ex_id, "mark":float(mark)}, ...],
#    "password":"pwd_to_enter_test" ,
#    "classrooms":[class_id1, class_id2, ....],
#    "public": boolean 
#    "deduct": decimal(4, 2) between 0 and 100 (is a percentage)
#    "timer": "02:00"(string) (HH:mm)
#    "repeat": boolean
#} 
# NOTE: OPTIONAL FIELDS: "classroom"(default= no relation), "public"(default=True), "deduct"(default=0.0), "password"(default=null), "timer"(default=null), "repeat"(default=False)
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
#    "classrooms":[id_classroom1, id_classroom2, ...],
#    "public": boolean
#    "deduct": decimal(4, 2)
#    "timer": "02:00"(string)
#    "repeat": boolean
#}
# NOTE: all the fields are optional, if keyword "exercises" is present it must follow the structure above 
# NOTE: if you want the password to be null/None you must send "password":null
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
        exam_data = JSONParser().parse(request)
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
@allowed_users(["Student", "Teacher"])
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
# Receives JSON with the field "pass" OR if exam has no password no jSON is needed
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
@my_classroom_exam()
def student_exam_view(request, id_classroom, id_exam):
    try:
        exam = Exam.objects.get(id=id_exam)

        if exam.repeat and SubmittedExam.objects.filter(exam_classroom=exam.id, student=request.user.id).exists():
            return JsonResponse({ 'v': False, 'm': 'You have already submitted this exam' }, safe=False)

        if exam.password != None:
            data = JSONParser().parse(request)
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

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Student (user.role==1) can access
# Receives exam id trough URL
# Receives JSON with the fields:{
#    "final_mark":16.90,
#    "answers":{ ex_id: answer,
#                ex_id: answer,
#                ex_id: answer
#    }
#}
# If successful returns: {"v": true, "m": exam.id}
# If unsuccessful returns: { "v": False, "m": Error message } 
@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Student"])
@my_classroom_exam()
def submit_exam_view(request, id_classroom, id_exam):
    data = JSONParser().parse(request)
    try:
        if (not Exam.objects.get(id=id_exam).repeat) and SubmittedExam.objects.filter(submitted_exam=id_exam, student=request.user.id).exists():
            return JsonResponse({ 'v': False, 'm': 'You have already submitted this exam' }, safe=False)

        data["submitted_exam"] = id_exam
        data["exam_classroom"] = id_classroom
        data["student"] = request.user.id
        data["exam_token"] = str(request.user.id)+"$$"+str(id)+"&&"+str(datetime.now())
        submited_exam_serializer = AddSubmittedExamSerializer(data=data)
        if submited_exam_serializer.is_valid():
            submited_exam_serializer.validate(data=data)
            exam = submited_exam_serializer.save()
            return JsonResponse({ 'v': True, 'm': exam.id }, safe=False)
        return JsonResponse({ 'v': False, 'm': submited_exam_serializer.errors}, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# Returns the students and their marks for the exam
# If sucessfull returns [
#    {
#        "student": "student.id student.first_name student.last_name",
#        "final_mark": "decimal(4,2)"
#        "classroom_id": "classroom_id classroom_name",
#    },
#    ...]
# If no student submitted the exam returns empty list
# If unsuccessful returns: { "v": False, "m": Error message }
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@ownes_exam()
def get_exam_final_marks_view(request, id):
    try:
        lst=[]
        for object in SubmittedExam.objects.filter(submitted_exam__id=id).values('student', 'final_mark', 'exam_classroom'):
            if object['exam_classroom']:
                lst.append({ 
                    "student": str(object["student"])+" "+str(Account.objects.get(id=object["student"]).first_name)+" "+str(Account.objects.get(id=object["student"]).last_name),
                    "final_mark": object['final_mark'],
                    "classroom_id": str(object['exam_classroom'])+" "+str(Classroom.objects.get(id=object['exam_classroom']).name)
                })
        return JsonResponse(lst, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)

# Only authenticated users can access this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Only users who have the role Teacher (user.role==2) can access
# Returns the students and their marks for the exam
# If sucessfull returns [
#    {
#        "student": "student.id student.first_name student.last_name",
#        "final_mark": "decimal(4,2)"
#        "exam_id": "classroom_id classroom_name",
#    },
#    ...]
# If no student submitted the exam returns empty list
# If unsuccessful returns: { "v": False, "m": Error message }
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@my_classroom()
def get_classroom_exams_final_marks_view(request, id):
    try:
        lst=[]
        for object in SubmittedExam.objects.filter(exam_classroom_id=id).values('student', 'final_mark', 'submitted_exam'):
            lst.append({ 
                "student": str(object["student"])+" "+str(Account.objects.get(id=object["student"]).first_name)+" "+str(Account.objects.get(id=object["student"]).last_name),
                "final_mark": object['final_mark'],
                "exam_id": str(object['submitted_exam'])+" "+str(Exam.objects.get(id=object['submitted_exam']).name)
            })
        return JsonResponse(lst, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e)}, safe=False)
