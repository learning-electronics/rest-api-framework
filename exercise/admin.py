from django.contrib import admin

from exercise.models import Exercise, Theme

# Register your models here.
admin.site.register(Theme)
admin.site.register(Exercise)