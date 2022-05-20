from django.contrib import admin
from exam.models import Exam, Marks

class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "teacher", "classrooms_list", "date_created")
    search_fields = ["name", "id", "teacher__first_name", "teacher__last_name", "date_created", "classrooms__name"]
    readonly_fields = ("id", "password", "date_created")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def classrooms_list(self, obj):
        return ", ".join([classroom.name for classroom in obj.classrooms.all()])


# Register your models here.
admin.site.register(Exam, ExamAdmin)
admin.site.register(Marks)