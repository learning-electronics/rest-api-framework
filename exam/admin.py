from django.contrib import admin
from exam.models import Exam, Marks, SubmittedExam

class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "teacher", "classrooms_list", "date_created")
    search_fields = ["name", "id", "teacher__first_name", "teacher__last_name", "date_created", "classrooms__name"]
    readonly_fields = ("id", "password", "date_created")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def classrooms_list(self, obj):
        return ", ".join([classroom.name for classroom in obj.classrooms.all()])


class MarksAdmin(admin.ModelAdmin):
    list_display = ("exam", "exercise", "mark")
    search_fields = ["exam__name", "exam__id" "exercise", "mark"]

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class SubmittedExamAdmin(admin.ModelAdmin):
    list_display = ("submitted_exam", "student_full_name", "final_mark", "date_submitted")
    search_fields = ["submitted_exam__name", "student", "final_mark", "date_submitted"]
    readonly_fields = ("submitted_exam", "student", "final_mark", "date_submitted", "answers")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def student_full_name(self, obj):
        return obj.student.full_name()

# Register your models here.
admin.site.register(Exam, ExamAdmin)
admin.site.register(Marks, MarksAdmin)
admin.site.register(SubmittedExam, SubmittedExamAdmin)