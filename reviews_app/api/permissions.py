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
        return (request.user.is_authenticated and request.user.type == 'customer')


class IsReviewOwner(BasePermission):
    """Allow access only to the author of a review."""

    def has_object_permission(self, request, view, obj):
        """Check whether the user wrote the review.

        Args:
            request (Request): The HTTP request with the current user.
            view (APIView): The view being accessed.
            obj (Review): The review being accessed.

        Returns:
            bool: True if the user wrote the review, otherwise False.
        """
        return obj.reviewer_id == request.user.id
