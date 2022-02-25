from rest_framework.permissions import BasePermission
from rest_framework.exceptions import ValidationError

from .models import User


class IsAuthenticated(BasePermission):
    """
    Permission for authenticated users
    """
    def has_permission(self, request, view):
        """
        Acces only for authenticated users
        """
        return bool(request.user and request.user.is_authenticated)


class IsManagementTeam(BasePermission):
    """
    Access only for management team users
    Permission for team management users
    """
    message = "You are not a member of the management team. You do not have access authorization."

    def has_permission(self, request, view):

        user = request.user
        team = user.user_team

        if not team == 1:
            return False
        else:
            return True
