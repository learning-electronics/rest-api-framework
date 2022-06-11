from django.urls import path
from exercise.api.views import(
    add_exercise_view,
    delete_exercise_view,
    get_themes_view,
    get_units_view,
    update_exercise_img_view,
    update_exercise_view,
    get_exercises_view,
    get_my_exercises_view,
    get_exercises_by_theme_view,
    add_exercise_solver_view,
    add_exercise_doc_view,
    associate_classroom_view,
    desassociate_classroom_view,
    upload_data,
)

app_name = "exercise"

urlpatterns = [
    path("add_exercise", add_exercise_view, name="add_exercise"),
    path("add_exercise_solver", add_exercise_solver_view, name="add_exercise_solver"),
    path("add_exercise_doc", add_exercise_doc_view, name="add_exercise_doc"),
    path("associate_classroom/<int:id>", associate_classroom_view, name="associate_with_classroom"),
    path("desassociate_classroom/<int:id>", desassociate_classroom_view, name="desassociate_with_classroom"),  
    path("update_ex_img/<int:id>", update_exercise_img_view, name="update_ex_img"),
    path("themes", get_themes_view, name="themes"),
    path("units", get_units_view, name="units"),
    path("exercises", get_exercises_view, name="exercises"),
    path("my_exercises", get_my_exercises_view, name="my_exercises"),
    path("delete_exercise/<int:id>", delete_exercise_view, name="delete_exercise"),
    path("update_exercise/<int:id>", update_exercise_view, name="update_exercise"),
    path("exercises_by_theme/<int:id>", get_exercises_by_theme_view, name="exercises_by_theme"),
    path("upload_data", upload_data, name="upload_data"),
]
