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
    ClientListSerializer
)
from .permissions import IsAuthenticated, IsClientView
from .models import Client, Contract, Event, Company


class CompanyViewset(ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, IsClientView)

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
    permission_classes = (IsAuthenticated, IsClientView)

    def get_queryset(self):
        user = self.request.user
        clients = Client.objects.all()

        return clients

    def create(self, request, *args, **kwargs):
        client_data = request.data
        company = Company.objects.filter(name__iexact=client_data['company'])
        if not company:
            return Response({"Company": f"Company '{client_data['company']}"},
                            status=status.HTTP_404_NOT_FOUND)
        company = company.get()
        company_id = company.id
        data = {
            'first_name': client_data['first_name'],
            'last_name': client_data['last_name'],
            'email': client_data['email'],
            'phone': client_data['phone'],
            'mobile': client_data['mobile'],
            'company': company_id
        }
        client_serializer = ClientSerializer(data=data)
        if client_serializer.is_valid():

            client = client_serializer.save()

            return Response(client_serializer.data)
        return Response(client_serializer.errors)


    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        pass


class ContractViewset(ModelViewSet):
    pass


class EventViewset(ModelViewSet):
    pass
