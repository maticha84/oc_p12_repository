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


class IsSalesView(BasePermission):
    message = "You are not a member of the sales team. You do not have access authorization."

    def has_permission(self, request, view):
        user = request.user
        team = user.user_team

        if view.action in ['list', 'retrieve']:
            return True
        elif view.action in ['create', 'destroy']:
            if not team == 3:
                return False
            return True

        elif view.action in ['update']:
            if team == 1 or team == 3:
                return True
            return False


class IsEventView(BasePermission):
    message = "You are not allowed to do this action."

    def has_permission(self, request, view):
        user = request.user
        team = user.user_team
        if view.action in ['list', 'retrieve', 'update']:
            return True

        elif view.action in ['create']:
            if not team == 3:
                return False
            return True

        elif view.action in ['destroy']:
            if team == 2 or team == 3:
                return True
            return False
