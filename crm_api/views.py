from django.shortcuts import render
from django.db.models import RestrictedError
from django.db.utils import IntegrityError
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
    EventListSerializer,
    CompanySerializer,
    ClientListSerializer,
    ContractListSerializer,
)
from .filters import (
    ClientFilterSet,
    ContractFilterSet,
    EventFilterSet
)
from .permissions import IsAuthenticated, IsSalesView, IsEventView
from .models import Client, Contract, Event, Company
from authentication.models import User


class CompanyViewset(ModelViewSet):
    """
    Class for company viewset
    """
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, IsSalesView)

    def get_queryset(self):
        """
        Only authenticated users could get inforpmation about company object
        """
        user = self.request.user
        companies = Company.objects.all()

        return companies

    def create(self, request, *args, **kwargs):
        """
        Request method : POST
        Only sales member could create a new company.
        If serializer company is OK, creation of a Company object.
        :return: serializer.data or serializer.error
        """
        company_data = request.data
        serializer = CompanySerializer(data=company_data)

        if serializer.is_valid():
            company = serializer.save()
            company.save()
            serializer = CompanySerializer(company)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Only sales member could update a company object.
        if company object exists, serializer is tested
        If serializer company is OK, update of a Company object.
        :return: serializer.data or serializer.error
        """
        company = Company.objects.filter(pk=kwargs['pk'])
        if not company:
            return Response(
                {'Company': f"The company with the id {kwargs['pk']} doesn't exist. You can't update this."},
                status=status.HTTP_404_NOT_FOUND
            )

        company = company.get()
        company_data = request.data
        serializer = CompanySerializer(data=company_data, partial=True)

        if serializer.is_valid():
            if 'name' in company_data:
                company.name = company_data['name']

            company.save()
            serializer = CompanySerializer(company)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Only sales member could delete a company object.
        if company object exists, serializer is tested
        if clients are linked to company object, deletion is restricted.
        :return: serializer.data or serializer.error
        """
        company = Company.objects.filter(pk=kwargs['pk'])
        if not company:
            return Response(
                {'Company': f"The company with the id {kwargs['pk']} doesn't exist. You can't delete this."},
                status=status.HTTP_404_NOT_FOUND
            )

        company = company.get()
        try:
            company.delete()
            return Response(
                {'Deleted': f'The company with id {kwargs["pk"]} has been deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except RestrictedError:
            return Response(
                {'Restriction error': f'There are customers who belong to this company. '
                                      f'You must first delete the clients before deleting the company'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ClientViewset(ModelViewSet):
    """
    Class for view Client. Only get or retrieve http method.
    Only authenticated user could have access to.
    """
    serializer_class = ClientListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)
    http_method_names = ['get', 'retrieve', ]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ClientFilterSet

    def get_queryset(self):
        user = self.request.user
        clients = Client.objects.all()

        return clients


class ClientByCompanyViewset(ModelViewSet):
    """
    Class for client management. Only post, put or delete http method.
    Access for only authenticated user, with sales permission.
    """
    serializer_class = ClientListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)
    http_method_names = ['post', 'put', 'delete']

    def create(self, request, *args, **kwargs):
        """
        Creation of a Client object. Only a sales meber could do this action
        """
        client_data = request.data

        company = Company.objects.filter(id=kwargs['company_id'])
        if not company:
            return Response({"Company": f"Company '{kwargs['company_id']}' dosen't exist. "
                                        f"Please create this company before the client"},
                            status=status.HTTP_404_NOT_FOUND)
        company = company.get()

        client_serializer = ClientSerializer(data=client_data, partial=True)
        if client_serializer.is_valid():
            client = client_serializer.create(company=company, sales_contact=request.user)

            return Response(client, status=status.HTTP_201_CREATED)
        return Response(client_serializer.errors, status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update Client object. Only sales member responsible of the client object could update this,
        or a member of management team.
        """
        client_request_data = request.data
        client_to_modify = Client.objects.filter(pk=kwargs['pk'], company=kwargs['company_id'])
        user = request.user

        if not client_to_modify:
            return Response({"Client": f"Client with the id  '{kwargs['pk']}' doesn't exist in the company with"
                                       f"the ID '{kwargs['company_id']}'."
                                       f"You can't update this"},
                            status=status.HTTP_404_NOT_FOUND)
        client = client_to_modify.get()

        if user.user_team == 3 and user.id != client.sales_contact.id:
            return Response({"Sales User": f"You are not responsible for this client. You cannot change it"},
                            status=status.HTTP_403_FORBIDDEN)

        if 'sales_contact' in client_request_data:
            if user.user_team == 3:
                return Response({"Sales User": f"You are not allowed to change the customer's sales manager"},
                                status=status.HTTP_403_FORBIDDEN)
            sales_contact = User.objects.filter(email=client_request_data['sales_contact'], user_team=3)
            if not sales_contact:
                return Response({"Sales Contact": f"Sales contact {data['sales_contact']} in not available."},
                                status=status.HTTP_404_NOT_FOUND)

            contact = sales_contact.get()
            client.sales_contact = contact
            client.save()

        data = {}
        for key in client_request_data:
            if key != 'sales_contact':
                data[key] = client_request_data[key]

        serializer = ClientSerializer(data=data, partial=True)
        if serializer.is_valid():
            client_modify = serializer.update(instance=client, validated_data=data)
            client_modified = ClientSerializer(instance=client_modify).data

            return Response(client_modified, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
         Update Client object. Only sales member responsible of the client object could update this
         if contracts are linked to a client object, deleting is restricted
        """
        user = request.user
        client_to_destroy = Client.objects.filter(pk=kwargs['pk'], company=kwargs['company_id'])

        if not client_to_destroy:
            return Response({"Client": "Client with the id  '{kwargs['pk']}' doesn't exist in the company with"
                                       f"the ID '{kwargs['company_id']}'."
                                       f"You can't delete this"},
                            status=status.HTTP_404_NOT_FOUND)

        client_to_destroy = client_to_destroy.get()
        if user.user_team == 3 and user.id != client_to_destroy.sales_contact.id:
            return Response({"Sales User": f"You are not responsible for this client. You cannot delete it"},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            client_to_destroy.delete()
            return Response(
                {'Deleted': f'The client with id {kwargs["pk"]} has been deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except RestrictedError:
            return Response(
                {'Restriction error': f'Contracts are attached to this client. '
                                      f'Delete the associated contracts to remove this client.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContractViewset(ModelViewSet):
    """
    Class for view Contract. Only get or retrieve http method.
    Only authenticated user could have access to.
    """
    serializer_class = ContractListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)
    http_method_names = ['get', 'retrieve', ]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ContractFilterSet

    def get_queryset(self):
        user = self.request.user
        contracts = Contract.objects.all()

        return contracts


class ContractByClientViewset(ModelViewSet):
    """
    Class for contract management. Only post, put or delete http method.
    Access for only authenticated user, with sales permission.
    """
    serializer_class = ContractListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)
    http_method_names = ['post', 'put', 'delete']

    def create(self, request, *args, **kwargs):
        """
        Creation of a contrct object.
        Only member sales responsible of the client could create a contract linked to the client.
        If a contract is created, the client will be activated status.
        """
        contract_data = request.data
        client = Client.objects.filter(id=kwargs['client_id'])
        if not client:
            return Response({"Client": f"Client '{kwargs['client_id']}' dosen't exist. "
                                       f"Please create this client before the contract"},
                            status=status.HTTP_404_NOT_FOUND)
        client = client.get()
        if client.sales_contact != request.user:
            return Response({"Sales User": f"You are not responsible for this client. You cannot add a contract"
                                           f"to it. Only {client.sales_contact.email} can do this"},
                            status=status.HTTP_403_FORBIDDEN)
        contract_serializer = ContractSerializer(data=contract_data, partial=True)
        if contract_serializer.is_valid():
            contract = contract_serializer.create(sales_contact=request.user, client=client)
            if not client.is_active:
                client.is_active = True
                client.save()
            return Response(contract, status=status.HTTP_201_CREATED)
        return Response(contract_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Only member sales responsible of contract could update a contract, or a member of management team.
        """
        contract_data = request.data
        contract = Contract.objects.filter(pk=kwargs['pk'], client=kwargs['client_id'])
        if not contract:
            return Response({"Contract": f"Contract '{kwargs['pk']}' dosen't exist. "
                                         f"Please create this contract before update this"},
                            status=status.HTTP_404_NOT_FOUND)
        contract = contract.get()
        if contract.sales_contact != request.user and request.user.user_team == 3:
            return Response({"Sales User": f"You are not responsible for this client. You cannot modify a contract"
                                           f"to it. Only {contract.sales_contact.email} can do this"},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = ContractSerializer(data=contract_data, partial=True)
        if serializer.is_valid():
            contract_modify = serializer.update(instance=contract, validated_data=contract_data)
            contract_modified = ContractSerializer(instance=contract_modify).data
            return Response(contract_modified, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Onlys sales member responsible of the contract could be delete a contract.
        If an event is linked to a contract, deleting is restricted.
        """
        user = request.user
        contract = Contract.objects.filter(pk=kwargs['pk'], client=kwargs['client_id'])

        if not contract:
            return Response({"Contract": f"Contract with the id  '{kwargs['pk']}' for Client with the ID "
                                         f"'{kwargs['client_id']}'doesn't exist. "
                                         f"You can't delete this"},
                            status=status.HTTP_404_NOT_FOUND)
        contract = contract.get()
        client = contract.client

        if contract.sales_contact != user:
            return Response({"Sales User": f"You are not responsible for this client. You cannot delete a contract"
                                           f"to it. Only {contract.sales_contact.email} can do this"},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            contract.delete()
            if len(client.client_contract.all()) == 0:
                client.is_active = False
                client.save()
            return Response(
                {'Deleted': f'The contract with id {kwargs["pk"]} has been deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except RestrictedError:
            return Response(
                {'Restriction error': f'Event is attached to this contract. '
                                      f'Delete the associated event to remove this contract.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EventViewset(ModelViewSet):
    """
    Class for view Event. Only get or retrieve http method.
    Only authenticated user could have access to.
    """
    serializer_class = EventListSerializer
    permission_classes = (IsAuthenticated, IsEventView)
    http_method_names = ['get', 'retrieve', ]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EventFilterSet

    def get_queryset(self):
        user = self.request.user
        events = Event.objects.all()

        return events


class EventByContractViewset(ModelViewSet):
    """
    Class for client management. Only post, put or delete http method.
    Access for only authenticated user, with event permission.
    """
    serializer_class = EventListSerializer
    permission_classes = (IsAuthenticated, IsEventView)
    http_method_names = ['post', 'put', 'delete']

    def create(self, request, *args, **kwargs):
        """
        onlu member sales responsible of contract could create an event.
        it will activate contract
        Only one event per contract.
        """
        event_data = request.data
        contract = Contract.objects.filter(id=kwargs['contract_id'])
        if not contract:
            return Response({"Contract": f"Contract '{kwargs['contract_id']}' dosen't exist. "
                                         f"Please create this contract before the event"},
                            status=status.HTTP_404_NOT_FOUND)
        contract = contract.get()
        if contract.sales_contact != request.user:
            return Response({"Request user": f"You're not allowed to create this event. "
                                             f"Only {contract.sales_contact.email} is allowed to do this."},
                            status=status.HTTP_403_FORBIDDEN)
        event_serializer = EventSerializer(data=event_data, partial=True)

        if event_serializer.is_valid():
            try:
                event = event_serializer.create(contract=contract)
                contract.status = True
                contract.save()
                return Response(event, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"Contract": f"Contract '{kwargs['contract_id']}' has already an attached event. "
                                             f"Please choose another contract"},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Only member of management team could assign an event to a support contact.
        If event is assigned, only member of team management or support contact linked to this event could update this.
        If event is not assigned,  only member of team management or sales contact linked to this event could
        update this.
        Only support contact could modify status event.
        If no support contact : status is "not attributed" (1)
        """
        event_data = request.data
        user = request.user
        event = Event.objects.filter(pk=kwargs['pk'], contract=kwargs['contract_id'])

        if not event:
            return Response({"Event": f"Event '{kwargs['pk']}' dosen't exist. "
                                      f"Please create this event before update this"},
                            status=status.HTTP_404_NOT_FOUND)
        event = event.get()
        support_user = event.support_contact
        sales_user = event.contract.sales_contact

        if support_user is None:
            if user != sales_user and user.user_team != 1:
                return Response({"Request user": f"You're not allowed to update this event. "
                                                 f"Only {sales_user.email} or a member of the management team can "
                                                 f"update this event"},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            if user != support_user and user.user_team != 1:
                return Response({"Request user": f"You're not allowed to update this event."
                                                 f"Only {support_user.email} or a member of the management team can "
                                                 f"update this event"},
                                status=status.HTTP_403_FORBIDDEN)

        data_event = {}

        if 'support_contact' in event_data and user.user_team != 1:
            return Response({"Support contact": "You're not allowed to attached a user support to this event. "
                                                "Please contact the management team."},
                            status=status.HTTP_403_FORBIDDEN)
        elif 'support_contact' in event_data and user.user_team == 1:
            support_user = User.objects.filter(email=event_data['support_contact'], user_team=2)
            if not support_user:
                return Response({"Support contact": f"User support with email '{event_data['support_contact']}' "
                                                    f"doesn't exit. You can't assigned it to this event."},
                                status=status.HTTP_404_NOT_FOUND)
            support_user = support_user.get()
            event.support_contact = support_user
            event.status = 2
            event.save()
            for key in event_data:
                if not key == 'support_contact':
                    data_event[key] = event_data[key]
        else:
            data_event = event_data

        if 'status' in event_data:
            if support_user is None or user != support_user:
                return Response({"Status Event": "You're not allowed to modify status Event."},
                                status=status.HTTP_403_FORBIDDEN)

        serializer = EventSerializer(data=data_event, partial=True)
        if serializer.is_valid():
            event_modify = serializer.update(instance=event, validated_data=data_event)
            event_modified = EventSerializer(instance=event_modify).data
            return Response(event_modified, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        If event is assigned, only support contact linked to this event could delete this.
        If event is not assigned,  only sales contact linked to this event could delete this.
        when an event is deleted, contract assigned before has a status = False
        """
        user = request.user
        event = Event.objects.filter(pk=kwargs['pk'], contract=kwargs['contract_id'])

        if not event:
            return Response({"Event": f"Event '{kwargs['pk']}' dosen't exist. "
                                      f"Please create this event before update this"},
                            status=status.HTTP_404_NOT_FOUND)
        event = event.get()
        contract = event.contract
        sales_user = event.contract.sales_contact

        if user != sales_user:
            return Response({"Request user": f"You're not allowed to delete this event. "
                                             f"Only {sales_user.email} is allowed to delete this event."},
                            status=status.HTTP_403_FORBIDDEN)

        event.delete()
        contract.status = False
        contract.save()
        return Response(
            {'Deleted': f'The event with id {kwargs["pk"]} has been deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
