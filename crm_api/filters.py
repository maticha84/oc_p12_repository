from django_filters import rest_framework as filters

from .models import Client, Contract, Event


class ClientFilterSet(filters.FilterSet):
    """ Implement filters to be used with ClientViewset"""

    company_name = filters.CharFilter(
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


class ContractFilterSet(filters.FilterSet):
    """ Implement filters to be used with ContractViewset"""

    company_name = filters.CharFilter(
        field_name='client', lookup_expr='company__name__icontains'
    )
    email = filters.CharFilter(
        field_name='client', lookup_expr='email__icontains'
    )
    date_contract = filters.DateTimeFilter(
        field_name='date_created', lookup_expr='gte'
    )
    amount = filters.NumberFilter(
        field_name='amount', lookup_expr='gte'
    )

    def filter_sort_by(self, queryset, name, value):
        values = value.lower().split(',')
        return queryset.order_by(*values)

    class Meta:
        model = Contract
        fields = [
            'client',
            'date_created',
            'amount',
        ]


class EventFilterSet(filters.FilterSet):
    """ Implement filters to be used with EventViewset"""

    company_name = filters.CharFilter(
        field_name='contract', lookup_expr='client__company__name__icontains'
    )
    email = filters.CharFilter(
        field_name='contract', lookup_expr='client__email__icontains'
    )
    date_event = filters.DateTimeFilter(
        field_name='date_event', lookup_expr='gte'
    )

    def filter_sort_by(self, queryset, name, value):
        values = value.lower().split(',')
        return queryset.order_by(*values)

    class Meta:
        model = Event
        fields = [
            'contract',
            'date_event',
        ]
