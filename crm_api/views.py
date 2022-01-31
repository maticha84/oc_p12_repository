from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import ClientSerializer, ContractSerializer, EventSerializer, CompanySerializer
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


class ClientViewset(ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated, IsClientView)

    def get_queryset(self):
        user = self.request.user
        clients = Client.objects.all()

        return clients

    def create(self, request, *args, **kwargs):

        client_data = request.data
        serializer = ClientSerializer(data=client_data, partial=True)

        if serializer.is_valid():
            company = Company.objects.filter(name__iexact=client_data['company'])
            if not company:
                return Response(
                    {"Company": f"This company : '{client_data['company']}' doesn't exist in the base. "
                                f"Please create the company before client."},
                    status=status.HTTP_404_NOT_FOUND)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractViewset(ModelViewSet):
    pass


class EventViewset(ModelViewSet):
    pass
