from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Проверка является владельцем или администратором
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj == request.user

        is_admin = request.user.is_superuser

        return is_owner or is_admin


class IsModerator(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user

        return is_owner
