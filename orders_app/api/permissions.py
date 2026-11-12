from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Allow access only to logged-in customer users."""

    def has_permission(self, request, view):
        """Check whether the user is logged in and a customer.

        Args:
            request (Request): The HTTP request with the current user.
            view (APIView): The view being accessed.

        Returns:
            bool: True if the user is a logged-in customer, otherwise False.
        """
        return (request.user.is_authenticated and request.user.type == "customer")


class IsBusinessOrderOwner(BasePermission):
    """Allow access only to the business user who received the order."""

    def has_object_permission(self, request, view, obj):
        """Check whether the user is the business user of the ordered offer.

        Args:
            request (Request): The HTTP request with the current user.
            view (APIView): The view being accessed.
            obj (Order): The order being accessed.

        Returns:
            bool: True if the user is a logged-in business user who owns
                the ordered offer, otherwise False.
        """
        return (
            request.user.is_authenticated
            and request.user.type == "business"
            and obj.offer_detail.offer.user_id == request.user.id
        )
