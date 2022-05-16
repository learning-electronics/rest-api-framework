from django.db import models
from account.models import Account
from exercise.models import Exercise
from django.contrib.auth.hashers import make_password

class Classroom(models.Model):
    id          = models.AutoField(primary_key=True, verbose_name="id")
    name        = models.CharField(max_length=200, unique=True, verbose_name="name")
    teacher     = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'role': 2}, verbose_name="teacher", related_name='teacher')
    students    = models.ManyToManyField(Account, verbose_name="students", related_name="students", blank=True, limit_choices_to={'role': 1})
    exercises   = models.ManyToManyField(Exercise, verbose_name="exercises", related_name="exercises", blank=True, default=None)
    date_created= models.DateField(verbose_name="date created", auto_now=True)
    password    = models.CharField(('password'), max_length=128)

    # hashes the password and saves the instance
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(Classroom, self).save(*args, **kwargs)

    # saves the instance without messing with the password field
    def save_no_pass(self, *args, **kwargs):
        super(Classroom, self).save(*args, **kwargs)
