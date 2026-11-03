from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.type == "customer")

    #braucht noch has_object_permission()