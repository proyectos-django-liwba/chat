# permissions.py
from rest_framework import permissions

class IsCommentCreatorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, or OPTIONS requests (read-only).
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user making the request is the creator of the comment.
        return obj.user_id == request.user
