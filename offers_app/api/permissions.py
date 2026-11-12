from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """Allow access only to logged-in business users."""

    def has_permission(self, request, view):
        """Check whether the user is logged in and a business user.

        Args:
            request (Request): The HTTP request with the current user.
            view (APIView): The view being accessed.

        Returns:
            bool: True if the user is a logged-in business user,
                otherwise False.
        """
        return (request.user.is_authenticated and request.user.type == "business")


class IsOfferOwner(BasePermission):
    """Allow access only to the owner of an offer."""

    def has_object_permission(self, request, view, obj):
        """Check whether the user owns the offer.

        Args:
            request (Request): The HTTP request with the current user.
            view (APIView): The view being accessed.
            obj (Offer): The offer being accessed.

        Returns:
            bool: True if the user created the offer, otherwise False.
        """
        return obj.user_id == request.user.id
