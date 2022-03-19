from django.contrib import admin
from classroom.models import Classroom

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "teacher", "get_students", "date_created")
    search_fields = ["name", "id", "teacher__first_name", "teacher__last_name", "date_created"]
    readonly_fields = ("id", "password", "date_created")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def get_students(self, obj):
        return "\n".join([student.full_name() for student in obj.students.all()])

admin.site.register(Classroom, ClassroomAdmin)

