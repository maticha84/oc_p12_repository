from django.contrib import admin
from django import forms

from .models import Company, Client, Contract, Event



@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)

    list_filter = ('name',)

    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ()

    def get_queryser(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_admin:
            return queryset
        if request.user.user_team == 1:
            return queryset

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.user_team == 1:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone',
                    'mobile', 'company', 'sales_contact', 'is_active')

    list_filter = ('email', 'company', 'sales_contact', 'is_active')

    search_fields = ('email', 'company', 'sales_contact', 'is_active')
    ordering = ('company', 'sales_contact')
    filter_horizontal = ()

    def get_queryser(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_admin:
            return queryset
        if request.user.user_team == 1:
            return queryset

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.user_team == 1:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


