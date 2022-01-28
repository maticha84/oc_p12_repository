from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegistrationViewset

router = routers.SimpleRouter()
router.register('registration', RegistrationViewset, basename='registration')

urlpatterns = [
    path('', include(router.urls)),

]