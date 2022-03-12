from django.urls import path
from exercise.api.views import(
    add_exercise_view
)

app_name = "exercise"

urlpatterns = [
    path("add_exercise", add_exercise_view, name="add_exercise"),
]
