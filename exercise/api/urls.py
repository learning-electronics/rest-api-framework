from django.urls import path
from exercise.api.views import(
    add_exercise_view,
    update_exercise_img_view
)

app_name = "exercise"

urlpatterns = [
    path("add_exercise", add_exercise_view, name="add_exercise"),
    path("update_ex_img", update_exercise_img_view, name="update_ex_img"),
]
