from django_filters import rest_framework as filters

from .models import Client, Contract


class ClientFilterSet(filters.FilterSet):
    """ Implement filters to be used with ClientViewset"""

    name_contains = filters.CharFilter(
        field_name='company', lookup_expr='name__icontains'
    )

    email = filters.CharFilter(
        field_name='email'
    )

    def filter_sort_by(self, queryset, name, value):
        values = value.lower().split(',')
        return queryset.order_by(*values)

    class Meta:
        model = Client
        fields = [
            'company',
            'email',
        ]
