from django.urls import path
from exercise.api.views import(
    add_exercise_view,
    delete_exercise_view,
    get_themes_view,
    get_units_view,
    update_exercise_img_view,
    update_exercise_view
)

app_name = "exercise"

urlpatterns = [
    path("add_exercise", add_exercise_view, name="add_exercise"),
    path("update_ex_img", update_exercise_img_view, name="update_ex_img"),
    path("themes", get_themes_view, name="themes"),
    path("units", get_units_view, name="units"),
    path("delete_exercise/<int:id>", delete_exercise_view, name="delete_exercise"),
    path("update_exercise/<int:id>", update_exercise_view, name="update_exercise"),
]
