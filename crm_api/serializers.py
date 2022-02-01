from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Company, Client, Contract, Event


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ['name']

    def validate_name(self, value):
        if Company.objects.filter(name__iexact=value).exists():
            raise ValidationError({'Company': f'This company name: "{value}" already exists'})
        return value


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone', 'mobile', 'date_created', 'date_updated', 'company']

    def validate_email(self, value):
        if Client.objects.filter(email=value).exists():
            raise ValidationError({'E-mail Error': f'This client e-mail: {value} already exists'})
        return value


class ClientPartialSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone', 'mobile', 'date_created', 'date_updated']

    def validate_email(self, value):
        if Client.objects.filter(email=value).exists():
            raise ValidationError({'E-mail Error': f'This client e-mail: {value} already exists'})
        return value

class ContractSerializer(ModelSerializer):
    class Meta:
        model = Contract
        fields = ['date_created', 'date_updated', 'status', 'amount', 'payment_due', 'sales_contact', 'client']


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ['status', 'contract', 'support_contact', 'date_created',
                  'date_updated', 'event_date ', 'attendees', 'note']
