from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import ClientViewset, ContractViewset, EventViewset, CompanyViewset

router_company = routers.SimpleRouter()
router_company.register('companies', CompanyViewset, basename='companies')

router_client = routers.SimpleRouter()
router_client.register('clients', ClientViewset, basename='clients')

router_contract = routers.SimpleRouter()
router_contract.register('contracts', ContractViewset, basename='contracts')

router_event = routers.SimpleRouter()
router_event.register('events', EventViewset, basename='events')

urlpatterns = [
    path('', include(router_company.urls)),
    path('', include(router_client.urls)),
    path('', include(router_contract.urls)),
    path('', include(router_event.urls)),
]
