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

    def get_queryset(self):
        user = self.request.user
        clients = Client.objects.all()

        return clients

    def create(self, request, *args, **kwargs):
        client_data = request.data
        company = Company.objects.filter(name__iexact=client_data['company'])
        if not company:
            return Response({"Company": f"Company '{client_data['company']} dosen't exist. "
                                        f"Please create this company before the client"},
                            status=status.HTTP_404_NOT_FOUND)
        company = company.get()
        company_id = company.id
        data = {
            'first_name': client_data['first_name'],
            'last_name': client_data['last_name'],
            'email': client_data['email'],
            'phone': client_data['phone'],
            'mobile': client_data['mobile'],
            'company': company_id,
            'sales_contact': request.user.id
        }
        client_serializer = ClientSerializer(data=data)

        if client_serializer.is_valid():
            client = client_serializer.save()

            return Response(client_serializer.data)
        return Response(client_serializer.errors)

    def update(self, request, *args, **kwargs):
        client_update_data = request.data
        client_to_modify = Client.objects.filter(pk=kwargs['pk'])
        user = request.user
        if not client_to_modify:
            return Response({"Client": f"Client with the id  '{kwargs['pk']} doesn't exist."
                                       f"You can't update this"},
                            status=status.HTTP_404_NOT_FOUND)
        client_to_modify = client_to_modify.get()
        if user.user_team == 3 and user.id != client_to_modify.sales_contact.id :
            return Response({"Sales User": f"You are not responsible for this client. You cannot change it"},
                            status=status.HTTP_403_FORBIDDEN)
        data = {}
        for key in client_update_data:
            data[key] = client_update_data[key]
        if 'email' in data:
            if data['email'] == client_to_modify.email:
                del data['email']

        if 'company' in data:
            company = Company.objects.filter(name__iexact=data['company'])
            if not company:
                return Response({"Company": f"Company '{data['company']} doesn't exist. "
                                            f"Please create this company before the client"},
                                status=status.HTTP_404_NOT_FOUND)
            company = company.get()
            data['company'] = company.id
            client_to_modify.company = company
        else:
            data['company'] = client_to_modify.company.id

        if 'sales_contact' in data:
            sales_contact = User.objects.filter(email=data['sales_contact'], user_team=3)
            if not sales_contact:
                return Response({"Sales Contact": f"Sales contact {data['sales_contact']} in not available."},
                                status=status.HTTP_404_NOT_FOUND)
            sales_contact = sales_contact.get()
            data['sales_contact'] = sales_contact.id
            client_to_modify.sales_contact = sales_contact
        else:
            data['sales_contact'] = client_to_modify.sales_contact.id

        serializer = ClientSerializer(data=data, partial=True)
        if serializer.is_valid():
            if 'last_name' in data:
                client_to_modify.last_name = data['last_name']
            if 'first_name' in data:
                client_to_modify.first_name = data['first_name']
            if 'email' in data:
                client_to_modify.email = data['email']
            if 'phone' in data:
                client_to_modify.phone = data['phone']
            if 'mobile' in data:
                client_to_modify.mobile = data['mobile']

            client_to_modify.save()
            serializer = ClientSerializer(client_to_modify)

            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        client_to_destroy = Client.objects.filter(pk=kwargs['pk'])

        if not client_to_destroy:
            return Response({"Client": f"Client with the id  '{kwargs['pk']} doesn't exist."
                                       f"You can't update this"},
                            status=status.HTTP_404_NOT_FOUND)

        client_to_destroy = client_to_destroy.get()
        if user.user_team == 3 and user.id != client_to_destroy.sales_contact.id :
            return Response({"Sales User": f"You are not responsible for this client. You cannot change it"},
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

    def get_queryset(self):
        user = self.request.user
        contracts = Contract.objects.all()

        return contracts



class EventViewset(ModelViewSet):
    pass
