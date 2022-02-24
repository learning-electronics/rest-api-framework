from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Manages the creations of users (normal users and superusers)
class AccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, birth_date, password):
        if not email:
            raise ValueError("User must have an email address")
        if not first_name or not last_name:
            raise ValueError("User must have a full name")
        if not birth_date:
            raise ValueError("User must have a date of birth")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
                email       = self.normalize_email(email),
                first_name  = first_name,
                last_name   = last_name,
                birth_date  = birth_date,
                password    = password,
        )
        user.set_password(password)     # sets password
        user.save(using=self._db)       # saves user
        return user

    def create_superuser(self, email, password, first_name="PRIMEIRO", last_name="ULTIMO", birth_date="2001-02-25"):
        if not email:
            raise ValueError("User must have an email address")
        if not first_name or not last_name:
            raise ValueError("User must have a full name")
        if not birth_date:
            raise ValueError("User must have a date of birth")
        if not password:
            raise ValueError("User must have a password")

        user = self.create_user(
                email       = self.normalize_email(email),
                first_name  = first_name,
                last_name   = last_name,
                birth_date  = birth_date,
                password    = password
        )
        
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

# Customized User Model
class Account(AbstractBaseUser):
    email       = models.EmailField(verbose_name="email", max_length=120, unique=True)
    first_name  = models.CharField(verbose_name="first name", max_length=45)
    last_name   = models.CharField(verbose_name="last name", max_length=45)
    birth_date  = models.DateField(verbose_name="birth date")
    date_joined = models.DateField(verbose_name="date joined", auto_now=True)
    last_login  = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin    = models.BooleanField(default=False)
    is_staff    = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    #MAYBE ADD PROFILE PHOTO? AND MAKE IT REQUIRED?
    #MAYBE IS_ACTIVE?

    # Uses email field as username
    USERNAME_FIELD = "email"
    # Required Fields to create an user
    REQUIRED = ["email", "first_name", "last_name", "birth_date",] 

    #Calls AccountManager to create new users
    objects = AccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
