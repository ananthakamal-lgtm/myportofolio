"""
Custom DRF Permission classes for portfolio authorization.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """
    Allows read-only access (GET, HEAD, OPTIONS) to any visitor,
    and restricts write operations strictly to the portfolio owner (superuser).
    """

    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """
    Enforces the 4-role access matrix on Experience endpoints:
    - Guest & Regular User: Read-only (GET, HEAD, OPTIONS).
    - Editor (member of 'Editor' group or has change_experience perm): Read + PUT/PATCH.
    - Portfolio Owner (superuser): Full access (Read, POST, PUT, PATCH, DELETE).
    """

    message = "Only the portfolio owner or an Editor can modify experiences."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and (
                request.user.groups.filter(name__iexact="Editor").exists()
                or request.user.has_perm("main.change_experience")
            )
        )
