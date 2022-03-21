from django.db import models
from account.models import Account
from django.contrib.auth.hashers import make_password

class Classroom(models.Model):
    id          = models.AutoField(primary_key=True, verbose_name="id")
    name        = models.CharField(max_length=200, unique=True, verbose_name="name")
    teacher     = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'role': 2}, verbose_name="teacher", related_name='teacher')
    students    = models.ManyToManyField(Account, verbose_name="students", related_name='student', blank=True)
    date_created= models.DateField(verbose_name="date created", auto_now=True)
    password    = models.CharField(('password'), max_length=128)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(Classroom, self).save(*args, **kwargs)