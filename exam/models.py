from django.db import models
from django.db import models
from account.models import Account
from exercise.models import Exercise
from classroom.models import Classroom
from django.contrib.auth.hashers import make_password

class Exam(models.Model):
    id          = models.AutoField(primary_key=True, verbose_name="id")
    name        = models.CharField(max_length=200, verbose_name="name")
    teacher     = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'role': 2}, verbose_name="teacher", related_name='exam_teacher')
    exercises   = models.ManyToManyField(Exercise, verbose_name="exercises", related_name="exam_exercises", blank=True, default=None)
    classrooms  = models.ManyToManyField(Classroom, verbose_name="classrooms", related_name="exam_classrooms", blank=True, default=None)
    marks       = models.JSONField(verbose_name="marks")
    date_created= models.DateField(verbose_name="date created", auto_now=True)
    password    = models.CharField(('password'), max_length=128)
    public      = models.BooleanField(verbose_name="public", default=True)

    # hashes the password and saves the instance
    def save_with_pass(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(Exam, self).save(*args, **kwargs)

    # saves the instance without messing with the password field
    def save_no_pass(self, *args, **kwargs):
        super(Exam, self).save(*args, **kwargs)