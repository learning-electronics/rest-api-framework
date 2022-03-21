from django.urls import path
from classroom.api.views import(
    add_classroom_view,
    get_classrooms_view,
    get_my_classrooms_view,
    get_info_classroom_view,
    delete_classroom_view,
    enter_classroom_view,
)

app_name = "classroom"

urlpatterns = [
    path("classrooms", get_classrooms_view, name="get_classrooms"),
    path("my_classrooms", get_my_classrooms_view, name="get_my_classrooms"),
    path("my_classrooms/<int:id>", get_info_classroom_view, name="get_my_classroom_info"),
    path("add_classroom", add_classroom_view, name="add_classroom"),
    path("delete_classroom/<int:id>", delete_classroom_view, name="delete_classroom"),
    path("enter_classroom/<int:id>", enter_classroom_view, name="enter_classroom"),
    #path("update_exercise/<int:id>", update_exercise_view, name="update_exercise"),
]
