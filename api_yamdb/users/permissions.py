from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для пользователей с ролью admin."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_staff))

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_staff))
