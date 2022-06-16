import csv
import re

from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.db import IntegrityError

from rest_framework.decorators import api_view, permission_classes, parser_classes, action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from account.api.decorators import allowed_users, ownes_exercise

from exercise.models import Exercise, Theme
from classroom.models import Classroom
from exercise.api.serializers import ExerciseSerializer, ThemeSerializer
from django.core.files.storage import default_storage
from exercise.api.utils import RULE_CHOICES

import pickle
import random, string

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location='tmp/')

from os.path import abspath,realpath,dirname,join
import sys
import os
project_path = dirname(dirname(dirname(dirname(realpath(__file__)))))
sys.path += [join(project_path,'CircuitSolver/preprocessor/')]
from mytopcaller import handler

from exercise.api.utils import get_exercise_dict, convert_xmf_to_png
import shutil


# Only authenticated teachers can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Receives a JSON with the following fields "theme", "question", "ans1", "ans2", "ans3", "correct", "unit", "visible" and optional "resol"(String) and "public"(Bool) 
# If sucessfull updates user data and returns: { "v": True, "m": ex.id }
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

            if exercise_data["public"] == False and 'visible' in exercise_data:
                for class_id in exercise_data["visible"]:
                    if request.user == Classroom.objects.get(id=class_id).teacher:
                        Classroom.objects.get(id=class_id).exercises.add(ex.id)
                    else:
                        # This error should never happen from the frontend
                        raise ValidationError("You are not the teacher of the classroom " + str(class_id))

            return JsonResponse({ 'v': True, 'm': ex.id }, safe=False)

        return JsonResponse({ 'v': False, 'm': exercise_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except ValidationError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@parser_classes([MultiPartParser, FormParser,])
def add_exercise_doc_view(request):
    try:
        doc_file = request.FILES['file']
        extension = doc_file.name.split('.')[-1]
        doc_file.name = str(request.user.id) + "_" + ''.join(random.choice(string.ascii_lowercase) for i in range(5)) + "." + extension
        file_path = default_storage.save(doc_file.name, doc_file)
        #convert_xmf_to_png(project_path+"/rest-api-framework/api/media/"+file_path.split('.')[0]+"_media/")
        error_string=''
        for exercise_dict in get_exercise_dict("/api/media/"+file_path):
            exercise_dict["teacher"] = request.user.id
            exercise_dict["unit"] = 'None'
            exercise_dict["theme"] = [1]
            img_name = exercise_dict.pop('img', None) 
            if request.data.get('public') is not None:
                exercise_dict["public"] = request.data.get('public')
            exercise_serializer = ExerciseSerializer(data=exercise_dict) 
            if exercise_serializer.is_valid():
                ex = exercise_serializer.save()
                if img_name is not None:
                    img_path = str(ex.id) + "." + img_name.split('.')[-1]

                    if not os.path.exists(project_path+"/rest-api-framework/api/media/exercises"):
                        os.makedirs(project_path+"/rest-api-framework/api/media/exercises")

                    shutil.copy(project_path+"/rest-api-framework/api/media/"+file_path.split('.')[0]+"_media/"+img_name.split('/')[-1] , project_path+"/rest-api-framework/api/media/exercises/"+img_path)
                    ex.img = project_path+"/rest-api-framework/api/media/exercises/"+img_path
                    ex.save()
            else:
                print(exercise_dict)
                
        #delete temporary files (with are no longer needed)
        shutil.rmtree(project_path+"/rest-api-framework/api/media/"+file_path.split('.')[0]+"_media/")
        default_storage.delete(file_path)
        
        return JsonResponse({ 'v': True, 'm': None }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
@parser_classes([MultiPartParser, FormParser,])
def add_exercise_solver_view(request):
    try:
        cir_file = request.FILES['cirpath']
        cir_file.name = str(request.user.id) + "_" + ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        file_path = default_storage.save(cir_file.name, cir_file)

        ex = handler("api/media/" + file_path, 
            request.user.id, 
            [int(i) for i in request.data.get("theme").replace("[","").replace("]","").split(",")], 
            request.data.get("question"), 
            request.data.get("public"), 
            request.data.get("target"), 
            request.data.get("freq"), 
            request.data.get("unit") if request.data.get("unit")!=None else None )

        default_storage.delete(cir_file.name)
        exercise_serializer = ExerciseSerializer(data=ex)
        if exercise_serializer.is_valid():
            ex = exercise_serializer.save()

            if request.data.get("public") == 'false' and 'visible' in request.data:
                for class_id in [int(i) for i in request.data.get("visible").split(",")]:
                    if request.user == Classroom.objects.get(id=class_id).teacher:
                        Classroom.objects.get(id=class_id).exercises.add(ex.id)
                    else:
                        # This error should never happen from the frontend
                        raise ValidationError("You are not the teacher of the classroom " + str(class_id))
                        
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
# If sucessfull returns a list of theme objects { "id", "name" }
# If unsuccessful returns: { "v": False, "m": Error message } 
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
        exercises = Exercise.objects.filter(public=True)
        ids = exercises.values_list('id', flat=True)

        reloaded_qs = Exercise.objects.all()
        reloaded_qs.query = pickle.loads(pickle.dumps(ids.query))
        exercise_serializer = ExerciseSerializer(exercises, many=True)

        if exercise_serializer.is_valid:
            for val, q in enumerate(reloaded_qs):
                exercise_serializer.data[val].update(q)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

    return JsonResponse(exercise_serializer.data, safe=False)

# Only authenticated users can acess this view aka in HTTP header add "Authorization": "Bearer " + generated_auth_token
# Returns a list of exercises created by the user
@csrf_exempt
@api_view(["GET", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def get_my_exercises_view(request):
    try:
        exercises = Exercise.objects.filter(teacher=request.user.id)
        ids = exercises.values_list('id', flat=True)
        
        reloaded_qs = Exercise.objects.all()
        reloaded_qs.query = pickle.loads(pickle.dumps(ids.query))
        exercise_serializer = ExerciseSerializer(exercises, many=True)

        if exercise_serializer.is_valid:
            for exercise in exercise_serializer.data:
                if Classroom.objects.filter(exercises__id=exercise["id"]).exists():
                    lst = []
                    for classroom in Classroom.objects.filter(exercises__id=exercise["id"]):
                        lst.append({'id': classroom.id, 'name': classroom.name})
                    exercise['visible'] = lst

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
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

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
        saved_img = exercise.img
        exercise_data = JSONParser().parse(request)
        exercise_serializer = ExerciseSerializer(instance=exercise, data=exercise_data, partial=True)
        
        if exercise_serializer.is_valid():
            exercise_serializer.update(exercise, exercise_serializer.validated_data)

            # The code below is dumb, nontheless it works.
            # There is probably a better way to do this.
            exercise.img = saved_img
            exercise.save()

            if 'visible' in exercise_data:
                # Add the new classrooms
                for class_id in exercise_data["visible"]:
                    if request.user == Classroom.objects.get(id=class_id).teacher:
                        Classroom.objects.get(id=class_id).exercises.add(id)
                    else:
                        # This error should never happen from the frontend
                        raise ValidationError("You are not the teacher of the classroom " + str(class_id))

                # Remove the old classrooms
                for class_id in list(set(Classroom.objects.filter(exercises__id=id).values_list('id', flat=True)) - set(exercise_data["visible"])):
                    if request.user == Classroom.objects.get(id=class_id).teacher:
                        Classroom.objects.get(id=class_id).exercises.remove(id)
                    else:
                        raise ValidationError("You are not the teacher of the classroom " + str(class_id))

                            # This error should never happen from the frontend
            return JsonResponse({ 'v': True, 'm': None}, safe=False)
        
        return JsonResponse({ 'v': False, 'm': exercise_serializer.errors }, safe=False)
    except IntegrityError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except ValidationError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except KeyError as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

@csrf_exempt
@api_view(["GET", ])
@permission_classes([AllowAny])
def get_exercises_by_theme_view(request, id):
	try:
		exercises = Exercise.objects.filter(theme=id, public=False)
		exercise_serializer = ExerciseSerializer(exercises, many=True)
	except BaseException as e:
		return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)
	
	return JsonResponse(exercise_serializer.data, safe=False)

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def associate_classroom_view(request, id):
    txt = ""
    try:
        data = JSONParser().parse(request)

        for class_id in data["visible"]:
            if request.user == Classroom.objects.get(id=class_id).teacher:
                Classroom.objects.get(id=class_id).exercises.add(id)
            else:
                txt += "You are not the teacher of the classroom " + Classroom.get(id=class_id).name + "\n"

        return JsonResponse({ 'v': True, 'm': txt }, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users(["Teacher"])
def desassociate_classroom_view(request, id):
    data = JSONParser().parse(request)
    try:
        for class_id in data["class"]:
            if request.user == Classroom.objects.get(id=class_id).teacher:
                Classroom.objects.get(id=class_id).exercises.remove(id)

        return JsonResponse({ 'v': True, 'm': None }, safe=False)
    except BaseException as e:
        return JsonResponse({ 'v': False, 'm': str(e) }, safe=False)


@csrf_exempt
@api_view(["POST", ])
@permission_classes([AllowAny])
def upload_data(request):
    file = request.FILES["file"]
    
    content = file.read()

    file_content = ContentFile(content)
    file_name = fs.save("_tmp.csv", file_content)
    tmp_file = fs.path(file_name)

    csv_file = open(tmp_file, errors="ignore")
    reader = csv.reader(csv_file)
    next(reader)

    theme_table = []
    for id_, row in enumerate(reader):
        (
            name,
        ) = row

        theme_table.append(
            Theme(
                name=name,
            )
        )
    
    Theme.objects.bulk_create(theme_table)

    return JsonResponse({ 'v': True, 'm': "Successfully uploaded the data" }, safe=False)

@csrf_exempt
@api_view(["POST", ])
@permission_classes([IsAuthenticated])
@allowed_users("Teacher")
def upload_exercises_data(request):
    file = request.FILES["file"]
    
    content = file.read()

    file_content = ContentFile(content)
    file_name = fs.save("_tmp.csv", file_content)
    tmp_file = fs.path(file_name)

    csv_file = open(tmp_file, errors="ignore")
    reader = csv.reader(csv_file)
    next(reader)

    excercises_table = []
    for id_, row in enumerate(reader):
        (
            theme,
            question,
            img,
            ans1,
            ans2,
            ans3,
            correct,
            unit,
        ) = row

        excercises_table.append(
            Exercise(
                teacher=request.user.id,
                theme=theme,
                question=question,
                img=project_path + img,
                ans1=ans1,
                ans2=ans2,
                ans3=ans3,
                correct=correct,
                unit=unit
            )
        )
    
    Exercise.objects.bulk_create(excercises_table)

    return JsonResponse({ 'v': True, 'm': "Successfully uploaded the data" }, safe=False)
