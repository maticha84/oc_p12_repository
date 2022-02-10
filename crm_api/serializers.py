from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField

from .models import Company, Client, Contract, Event
from authentication.serializers import UserSerializer


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
        fields = ['first_name', 'last_name', 'email', 'phone', 'mobile', 'date_created', 'date_updated',
                  'company', 'sales_contact']

    def create(self, company=None, sales_contact=None):
        client = Client(
            company=company,
            sales_contact=sales_contact,
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            email=self.validated_data['email'],
            phone=self.validated_data['phone'],
            mobile=self.validated_data['mobile']
        )
        client.save()
        client_serialized = ClientSerializer(instance=client).data
        return client_serialized

    """def update(self, instance, validated_data, sales_contact=None):
        if sales_contact is not None:
            instance.sales_contact = sales_contact
        if self.validated_data.get('first_name'):
            instance.first_name = self.validated_data['first_name']
        if self.validated_data.get('last_name'):
            instance.last_name = self.validated_data['last_name']
        if self.validated_data.get('email'):
            instance.email = self.validated_data['email']
        if self.validated_data.get('phone'):
            instance.phone = self.validated_data['phone']
        if self.validated_data.get('mobile'):
            instance.mobile = self.validated_data['mobile']
        instance.save()
        return """



    def validate_email(self, value):
        if Client.objects.filter(email=value).exists():
            raise ValidationError({'E-mail Error': f'This client e-mail: {value} already exists'})
        return value

    def validate_phone(self, value):
        if not value.isnumeric() or len(value) < 4 or len(value) > 15:
            raise ValidationError({"Phone Error": f"This phone number :'{value}' isn't correct."})
        return value

    def validate_mobile(self, value):
        if not value.isnumeric() or len(value) < 4 or len(value) > 15:
            raise ValidationError({"Mobile Error": f"This mobile number :'{value}' isn't correct."})
        return value


class ClientListSerializer(ModelSerializer):
    client_company = SerializerMethodField()
    sales = SerializerMethodField()

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone', 'mobile', 'date_created', 'date_updated',
                  'client_company', 'sales']

    def get_client_company(self, instance):
        queryset = instance.company
        serializer = CompanySerializer(queryset)
        return serializer.data

    def get_sales(self, instance):
        queryset = instance.sales_contact
        serializer = UserSerializer(queryset)
        return serializer.data

    def validate_email(self, value):
        if Client.objects.filter(email=value).exists():
            raise ValidationError({'E-mail Error': f'This client e-mail: {value} already exists'})
        return value


class ContractSerializer(ModelSerializer):
    class Meta:
        model = Contract
        fields = ['date_created', 'date_updated', 'status', 'amount', 'payment_due', 'sales_contact', 'client']

    def create(self, sales_contact=None, client=None):
        contract = Contract(
            sales_contact=sales_contact,
            client=client,
            amount=self.validated_data['amount'],
            payment_due=self.validated_data['payment_due']
        )
        contract.save()
        contract_serialized = ContractSerializer(instance=contract).data
        return contract_serialized


class ContractListSerializer(ModelSerializer):
    client_contract = SerializerMethodField()
    sales = SerializerMethodField()

    class Meta:
        model = Contract
        fields = ['date_created', 'date_updated', 'status', 'amount', 'payment_due', 'sales',
                  'client_contract']



    def get_client_contract(self, instance):
        queryset = instance.client
        serializer = ClientSerializer(queryset)
        return serializer.data

    def get_sales(self, instance):
        queryset = instance.sales_contact
        serializer = UserSerializer(queryset)
        return serializer.data


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ['status', 'contract', 'support_contact', 'date_created',
                  'date_updated', 'event_date ', 'attendees', 'note']
