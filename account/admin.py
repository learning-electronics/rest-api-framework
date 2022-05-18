from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account

class AccountAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "id", "last_login", "date_joined", "is_admin", "is_staff", "is_active")
    search_fields = ("email", "id", "first_name", "last_name")
    readonly_fields = ("id", "first_name", "last_name", "birth_date", "date_joined", "last_login")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)