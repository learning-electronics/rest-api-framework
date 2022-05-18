from django.urls import path
from exam.api.views import(
    add_exam_view,
    student_exam_view,
)

app_name = "exam"

urlpatterns = [
    #path("my_classrooms", get_my_classrooms_view, name="get_my_classrooms"),
    #path("my_classrooms/<int:id>", get_info_classroom_view, name="get_my_classroom_info"),
    #path("update_classroom/<int:id>", update_classroom_view, name="get_my_classroom_info"),
    #path("delete_classroom/<int:id>", delete_classroom_view, name="delete_classroom"),
    #path("classrooms", get_classrooms_view, name="get_classrooms"),
    path("add_exam", add_exam_view, name="add_exam"),
    path("student_exam/<int:id>", student_exam_view, name="student_exam"),
    #path("enter_classroom/<int:id>", enter_classroom_view, name="enter_classroom"),
    #path("exit_classroom/<int:id>", exit_classroom_view, name="exit_classroom"),
]
