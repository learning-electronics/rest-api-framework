from django.urls import path
from exam.api.views import(
    get_professor_exams_view,
    add_exam_view,
    delete_exam_view,
    update_exam_view,
    get_classroom_exams_view,
    student_exam_view,
)

app_name = "exam"

urlpatterns = [
    #path("my_classrooms", get_my_classrooms_view, name="get_my_classrooms"),
    #path("update_classroom/<int:id>", update_classroom_view, name="get_my_classroom_info"),
    path("professor/my_exams", get_professor_exams_view, name="professor_exams"),
    path("professor/add_exam", add_exam_view, name="add_exam"),
    path("professor/delete_exam/<int:id>", delete_exam_view, name="delete_exam"),
    path("professor/update_exam/<int:id>", update_exam_view, name="update_exam"),
    path("student/my_classroom/<int:id>/exams", get_classroom_exams_view, name="classroom_exams"),
    path("student/exam/<int:id>", student_exam_view, name="student_exam"),
    #path("classrooms", get_classrooms_view, name="get_classrooms"),
    #path("enter_classroom/<int:id>", enter_classroom_view, name="enter_classroom"),
    #path("exit_classroom/<int:id>", exit_classroom_view, name="exit_classroom"),
]
