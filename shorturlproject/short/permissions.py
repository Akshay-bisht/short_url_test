from rest_framework import permissions


class SolutionProviderPermission(permissions.BasePermission):
    """
    Custom permissions
    check the permission for the user is solution provider or not
    """
    def has_permission(self, request, view):
        if request.method in ['POST', 'GET']:
            if request.user.solution_provider or request.user.is_superuser:
                return True
        return False