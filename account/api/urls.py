from django.urls import path
from account.api.views import(
    login_view,
    logout_view,
    registration_view,
    change_password,
)

app_name = "account"

urlpatterns = [
    path("register", registration_view, name="register"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("change_pwd", change_password, name="change_pwd"),
]