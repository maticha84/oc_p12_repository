from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User


# Register your models here.

@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Group)
