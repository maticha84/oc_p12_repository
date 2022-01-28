from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import RegistrationSerializer
from .permissions import IsAuthenticated, IsManagementTeam


class RegistrationViewset(ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = (IsAuthenticated, IsManagementTeam)
    http_method_names = ['post', ]
