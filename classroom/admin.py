from django.contrib import admin
from classroom.models import Classroom

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "teacher", "students_list", "date_created")
    search_fields = ["name", "id", "teacher__first_name", "teacher__last_name", "date_created"]
    readonly_fields = ("id", "password", "date_created")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def students_list(self, obj):
        return ", ".join([student.full_name() for student in obj.students.all()])

admin.site.register(Classroom, ClassroomAdmin)

