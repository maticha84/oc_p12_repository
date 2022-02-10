from django.shortcuts import render
from django.db.models import RestrictedError
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
    CompanySerializer,
    ClientListSerializer,
    ContractListSerializer,
)
from .permissions import IsAuthenticated, IsSalesView
from .models import Client, Contract, Event, Company
from authentication.models import User


class CompanyViewset(ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, IsSalesView)

    def get_queryset(self):
        user = self.request.user
        companies = Company.objects.all()

        return companies

    def create(self, request, *args, **kwargs):
        company_data = request.data
        serializer = CompanySerializer(data=company_data)

        if serializer.is_valid():
            company = serializer.save()
            company.save()
            serializer = CompanySerializer(company)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
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
    serializer_class = ClientListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)
    http_method_names = ['get', 'retrieve', ]

    def get_queryset(self):
        user = self.request.user
        clients = Client.objects.all()

        return clients


class ClientByCompanyViewset(ModelViewSet):
    serializer_class = ClientListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)

    def get_queryset(self):
        user = self.request.user
        clients = Client.objects.filter(company_id=self.kwargs['company_id'])

        return clients

    def create(self, request, *args, **kwargs):
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
    serializer_class = ContractListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)
    http_method_names = ['get', 'retrieve', ]

    def get_queryset(self):
        user = self.request.user
        contracts = Contract.objects.all()

        return contracts


class ContractByClientViewset(ModelViewSet):
    serializer_class = ContractListSerializer
    permission_classes = (IsAuthenticated, IsSalesView)

    def get_queryset(self):
        user = self.request.user
        contracts = Contract.objects.filter(client_id=self.kwargs['client_id'])

        return contracts

    def create(self, request, *args, **kwargs):
        contract_data = request.data
        client = Client.objects.filter(id=kwargs['client_id'])
        if not client:
            return Response({"Client": f"Client '{kwargs['client_id']}' dosen't exist. "
                                       f"Please create this client before the contract"},
                            status=status.HTTP_404_NOT_FOUND)
        client = client.get()
        contract_serializer = ContractSerializer(data=contract_data, partial=True)
        if contract_serializer.is_valid():
            contract = contract_serializer.create(sales_contact=request.user, client=client)
            return Response(contract)
        return Response(contract_serializer.errors)

    def update(self, request, *args, **kwargs):
        contract_data = request.data
        client = Client.objects.filter(pk=kwargs['client_id'])
        if not client:
            return Response({"Client": f"Client '{kwargs['client_id']}' dosen't exist. "
                                       f"Please create this client before the contract"},
                            status=status.HTTP_404_NOT_FOUND)
        contract = Contract.objects.filter(pk=kwargs['pk'])
        if not contract:
            return Response({"Contract": f"Contract '{kwargs['pk']}' dosen't exist. "
                                         f"Please create this contract before update this"},
                            status=status.HTTP_404_NOT_FOUND)
        contract = contract.get()
        serializer = ContractSerializer(data=contract_data, partial=True)
        if serializer.is_valid():
            contract_modify = serializer.update(instance=contract, validated_data=contract_data)
            contract_modified = ContractSerializer(instance=contract_modify).data
            return Response(contract_modified, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        contract = Contract.objects.filter(pk=kwargs['pk'], client=kwargs['client_id'])

        if not contract:
            return Response({"Contract": f"Contract with the id  '{kwargs['pk']}' for Client with the ID "
                                         f"'{kwargs['client_id']}'doesn't exist. " 
                                         f"You can't delete this"},
                            status=status.HTTP_404_NOT_FOUND)
        contract = contract.get()
        if user.user_team == 3 and user.id != contract.sales_contact.id:
            return Response({"Sales User": f"You are not responsible for this client. You cannot change it"},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            contract.delete()
            return Response(
                {'Deleted': f'The contract with id {kwargs["pk"]} has been deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except RestrictedError:
            return Response(
                {'Restriction error': f'Event is attached to this contract. '
                                      f'Delete the associated event to remove this client.'},
                status=status.HTTP_400_BAD_REQUEST
            )



class EventViewset(ModelViewSet):
    pass
