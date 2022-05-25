from django.urls import path
from exam.api.views import(
    get_professor_exams_view,
    get_professor_exam_info_view,
    add_exam_view,
    delete_exam_view,
    update_exam_view,
    get_classroom_exams_view,
    student_exam_view,
    submit_exam_view,
)

app_name = "exam"

urlpatterns = [
    path("professor/my_exams", get_professor_exams_view, name="professor_exams"),
    path("professor/my_exams/exam/<int:id>", get_professor_exam_info_view, name="professor_exams"),
    path("professor/my_exams/add_exam", add_exam_view, name="add_exam"),
    path("professor/my_exams/delete_exam/<int:id>", delete_exam_view, name="delete_exam"),
    path("professor/my_exams/update_exam/<int:id>", update_exam_view, name="update_exam"),
    path("student/my_classroom/<int:id>/exams", get_classroom_exams_view, name="classroom_exams"),
    path("student/exam/<int:id>", student_exam_view, name="student_exam"),
    path("student/exam/<int:id>/submit_exam", submit_exam_view, name="submit_exam"),
]
