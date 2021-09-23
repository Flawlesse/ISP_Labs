from rest_framework import permissions

class IsSameUserAccountOrReadonly(permissions.IsAuthenticatedOrReadOnly):
    "For Account model used."
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user == obj
        )


class IsSameAsAuthorOrReadonly(permissions.IsAuthenticatedOrReadOnly):
    "For Order model used."
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user == obj.author
        )
