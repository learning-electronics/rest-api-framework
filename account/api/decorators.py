from django.http.response import JsonResponse
from account.models import Account

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