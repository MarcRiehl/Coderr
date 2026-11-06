from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.type == "customer")

class IsBusinessOrderOwner(BasePermission): #für Patch

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.type == "business"
            and obj.offer_detail.offer.user_id == request.user.id
        )