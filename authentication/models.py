from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class ManageUser(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Email is missing")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.save()
        return user


class User(AbstractBaseUser):
    USER_TEAM_CHOICES = (
        (1, 'management'),
        (2, 'support'),
        (3, 'sales'),
    )
    user_team = models.PositiveSmallIntegerField(choices=USER_TEAM_CHOICES, default=1)
    first_name = models.CharField(max_length=25, verbose_name="First Name")
    last_name = models.CharField(max_length=25, verbose_name="Last Name")
    email = models.EmailField(unique=True, max_length=100, verbose_name="E-Mail")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = ManageUser()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

