from django.urls import path
from classroom.api.views import(
    add_classroom_view,
    get_classes_view,
)

app_name = "classroom"

urlpatterns = [
    path("classrooms", get_classes_view, name="get_classrooms"),
    path("add_classroom", add_classroom_view, name="add_classroom"),
    #path("update_exercise/<int:id>", update_exercise_view, name="update_exercise"),
]
