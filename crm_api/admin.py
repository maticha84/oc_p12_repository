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
    readonly_fields = ('is_active', )
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


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'client', )
    list_display = ('id', 'date_created', 'date_updated', 'client', 'sales_contact',
                    'amount', 'payment_due', 'status')

    list_filter = ('client', 'amount', 'payment_due', 'sales_contact', 'status')

    search_fields = ('id', 'client', 'date_created', 'sales_contact', 'amount')
    ordering = ('id', 'date_created', 'client')
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


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('contract', 'date_created', 'date_updated')
    list_display = ('id', 'date_created', 'date_updated', 'contract', 'status', 'date_event',
                    'support_contact', 'attendees', 'note')

    list_filter = ('support_contact', 'status', 'date_event', 'contract')

    search_fields = ('id', 'contract', 'status', 'support_contact')
    ordering = ('id', 'date_created', 'contract')
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

    def save_model(self, request, obj, form, change):
        if obj.support_contact is None:
            obj.status = 1
        elif obj.support_contact is not None and obj.status == 1:
            obj.status = 2
        super().save_model(request, obj, form, change)
