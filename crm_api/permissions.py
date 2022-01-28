from rest_framework.permissions import BasePermission
from rest_framework.exceptions import ValidationError

from authentication.models import User


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        """
        Acces only for authenticated users
        """
        return bool(request.user and request.user.is_authenticated)


class IsManagementTeam(BasePermission):
    """
    Access only for management team users
    """
    message = "You are not a member of the management team. You do not have access authorization."

    def has_permission(self, request, view):

        user = request.user
        team = user.user_team

        if not team == 1:
            return False
        else:
            return True


class IsSupportTeam(BasePermission):
    """
        Access only for support team users
        """
    message = "You are not a member of the support team. You do not have access authorization."

    def has_permission(self, request, view):

        user = request.user
        team = user.user_team

        if not team == 2:
            return False
        else:
            return True


class IsSalesTeam(BasePermission):
    """
        Access only for sales team users
        """
    message = "You are not a member of the sales team. You do not have access authorization."

    def has_permission(self, request, view):

        user = request.user
        team = user.user_team

        if not team == 3:
            return False
        else:
            return True
