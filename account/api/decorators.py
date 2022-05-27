from django.http.response import JsonResponse
from account.models import Account
from exercise.models import Exercise
from classroom.models import Classroom
from exam.models import Exam

# Only allow users to acess the view_func if their role is on the list
# [ (Teacher, 2) or (Student, 1) or (Deleted, 0) ]
# If sucessfull it returns (allows) the user to access the view_func
# If unsuccessful returns: { "v": False, "m": Error message } 
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            account = Account.objects.get(email= request.user)
            role = "Student" if account.role==1 else "Teacher" if account.role==2 else "Deleted"
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({ 'v': False, 'm': "Invalid Role" }, safe=False)
        return wrapper_func
    return decorator

# Checks if the given user (Teacher) is the author/owner of the exercise
# If sucessfull it returns (allows) the user to access the view_func
# If unsuccessful returns: { "v": False, "m": Error message }  
def ownes_exercise():
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if not Exercise.objects.filter(id=kwargs['id']).exists():
                return JsonResponse({ 'v': False, 'm': "Doesn't Exist" }, safe=False)

            if Account.objects.get(email= request.user).id == Exercise.objects.get(id=kwargs['id']).teacher.id:
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({ 'v': False, 'm': "Not your exercise" }, safe=False)
        return wrapper_func
    return decorator

# Checks if the given user (Teacher) is the author/owner of the exam
# If sucessfull it returns (allows) the user to access the view_func
# If unsuccessful returns: { "v": False, "m": Error message }  
def ownes_exam():
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if not Exam.objects.filter(id=kwargs['id']).exists():
                return JsonResponse({ 'v': False, 'm': "Doesn't Exist" }, safe=False)

            if Account.objects.get(email= request.user).id == Exam.objects.get(id=kwargs['id']).teacher.id:
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({ 'v': False, 'm': "Not your exam" }, safe=False)
        return wrapper_func
    return decorator
    
# Checks if the classroom belongs to the teacher(user.role==2)
# Checks if the student belongs to the classroom(user.role==1)
# If sucessfull it returns (allows) the user to access the view_func
# If unsuccessful returns: { "v": False, "m": Error message }  
def my_classroom():
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if not Classroom.objects.filter(id=kwargs['id']).exists():
                return JsonResponse({ 'v': False, 'm': "Doesn't Exist" }, safe=False)

            if (request.user.role == 1 and request.user.students.filter(id=kwargs['id']).exists()) or (request.user.role == 2 and request.user.teacher.filter(id=kwargs['id']).exists()):
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({ 'v': False, 'm': "Not your classroom" }, safe=False)
        return wrapper_func
    return decorator

# Checks if the classroom and the exam are associated
# If sucessfull it returns (allows) the user to access the view_func
# If unsuccessful returns: { "v": False, "m": Error message } 
def my_classroom_exam():
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if not Classroom.objects.filter(id=kwargs['id_classroom']).exists():
                return JsonResponse({ 'v': False, 'm': "Doesn't Exist" }, safe=False)

            if not Exam.objects.filter(id=kwargs['id_exam']).exists():
                if Exam.objects.get(id=kwargs['id_exam']).public==False:
                    return JsonResponse({ 'v': False, 'm': "Doesn't Exist" }, safe=False)

            if not Exam.objects.filter(id=kwargs['id_exam'], classrooms__id=kwargs['id_classroom']).exists():
                return JsonResponse({ 'v': False, 'm': "Not Associated" }, safe=False)

            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator