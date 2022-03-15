from django.db import models
from account.models import Account
from exercise.api.utils import RULE_CHOICES
    
class Theme(models.Model):
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=200)

class Exercise(models.Model):
    id          = models.AutoField(primary_key=True, verbose_name="id")
    teacher     = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, limit_choices_to={'role': 2}, verbose_name="teacher id")
    theme       = models.ManyToManyField(Theme, verbose_name="theme id")
    question    = models.CharField(max_length=500, verbose_name="question")
    img         = models.ImageField(max_length=100, null=True, blank=True, verbose_name="image")
    ans1        = models.CharField(max_length=10, verbose_name="answer 1")
    ans2        = models.CharField(max_length=10, verbose_name="answer 2")
    ans3        = models.CharField(max_length=10, verbose_name="answer 3")
    correct     = models.CharField(max_length=10, verbose_name="correct answer")
    unit        = models.CharField(max_length=5, choices=RULE_CHOICES, verbose_name="unit")
    resol       = models.CharField(max_length=500, null=True, blank=True, verbose_name="resolution")
