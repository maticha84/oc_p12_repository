from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ClientViewset,
    ClientByCompanyViewset,
    ContractViewset,
    ContractByClientViewset,
    EventViewset,
    EventByContractViewset,
    CompanyViewset
)

router_company = routers.SimpleRouter()
router_company.register('companies', CompanyViewset, basename='companies')

router_client = routers.SimpleRouter()
router_client.register('clients', ClientViewset, basename='clients')
router_client_company = routers.SimpleRouter()
router_client_company.register('client_by_company', ClientByCompanyViewset, basename='client_by_company')

router_contract = routers.SimpleRouter()
router_contract.register('contracts', ContractViewset, basename='contracts')
router_contract_client = routers.SimpleRouter()
router_contract_client.register('contracts_by_client', ContractByClientViewset, basename='contracts_by_client')
router_event = routers.SimpleRouter()
router_event.register('events', EventViewset, basename='events')
router_event_contract = routers.SimpleRouter()
router_event_contract.register('event_by_contract', EventByContractViewset, basename='event_by_contract')

urlpatterns = [
    path('', include(router_company.urls)),
    path('companies/<int:company_id>/', include(router_client_company.urls)),
    path('', include(router_client.urls)),
    path('', include(router_contract.urls)),
    path('clients/<int:client_id>/', include(router_contract_client.urls)),
    path('', include(router_event.urls)),
    path('contracts/<int:contract_id>/', include(router_event_contract.urls)),
]
