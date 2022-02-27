from django.urls import path


from account.api.views import(
    delete_view,
    login_view,
    logout_view,
    profile_view,
    registration_view,
    change_password,
    update_profile,
    upload_avatar,
    activate_account,
)

app_name = "account"

urlpatterns = [
    path("register", registration_view, name="register"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("change_pwd", change_password, name="change_pwd"),
    path("user", profile_view, name="get_profile"),
    path("delete", delete_view, name="delte_view"),
    path("update_user", update_profile, name="update_profile"),
    path("upload_avatar", upload_avatar, name="upload_avatar"),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', activate_account, name='activate'),
] 
