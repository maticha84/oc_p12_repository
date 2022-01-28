from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ClientSerializer, ContractSerializer, EventSerializer


class ClientViewset(ModelViewSet):
    pass


class ContractViewset(ModelViewSet):
    pass


class EventViewset(ModelViewSet):
    pass
