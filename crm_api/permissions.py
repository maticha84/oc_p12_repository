from rest_framework.permissions import BasePermission
from rest_framework.exceptions import ValidationError

from authentication.models import User


class IsAuthenticated(BasePermission):
    """
        Permission for authenticated users
    """
    def has_permission(self, request, view):
        """
        Acces only for authenticated users
        """
        return bool(request.user and request.user.is_authenticated)


class IsSalesView(BasePermission):
    """
        Permission for sales users, in charge of client or contract
    """
    message = "You are not allowed to do this action."

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
    """
        Permission for support or sales users in charge of event
    """
    message = "You are not allowed to do this action."

    def has_permission(self, request, view):
        user = request.user
        team = user.user_team
        if view.action in ['list', 'retrieve', 'update']:
            return True

        elif view.action in ['create', 'destroy']:
            if not team == 3:
                return False
            return True

