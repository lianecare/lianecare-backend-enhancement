from rest_framework import permissions

from lianecare.solace.models import CaregiverPro


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user


class IsOwnerCaregiverOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            caregiver = CaregiverPro.objects.get(username=request.user.username)
            return obj.caregiver == caregiver
        except CaregiverPro.DoesNotExist:
            return False


class IsOwnerOfJP(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an Job Post to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            caregiver = CaregiverPro.objects.get(username=request.user.username)
            return obj.caregiver == caregiver
        except CaregiverPro.DoesNotExist:
            return False
