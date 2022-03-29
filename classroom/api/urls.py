from django.urls import path
from classroom.api.views import(
    add_classroom_view,
    get_classrooms_view,
    get_my_classrooms_view,
    get_info_classroom_view,
    delete_classroom_view,
    enter_classroom_view,
    update_classroom_view,
)

app_name = "classroom"

urlpatterns = [
    path("my_classrooms", get_my_classrooms_view, name="get_my_classrooms"),
    path("my_classrooms/<int:id>", get_info_classroom_view, name="get_my_classroom_info"),
    path("my_classrooms/<int:id>/update_classroom", update_classroom_view, name="get_my_classroom_info"),
    path("my_classrooms/<int:id>/delete_classroom", delete_classroom_view, name="delete_classroom"),
    path("classrooms", get_classrooms_view, name="get_classrooms"),
    path("classrooms/add_classroom", add_classroom_view, name="add_classroom"),
    path("classrooms/enter_classroom/<int:id>", enter_classroom_view, name="enter_classroom"),
]
