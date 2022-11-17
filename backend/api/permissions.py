from rest_framework import permissions


class CustomBasePermission(permissions.BasePermission):
    message = 'Вы не обладаете достаточными правами для данной операции!'


class IsAuthenticatedAndOwnerOrAdmin(CustomBasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or (request.user == obj) or (
                    request.user == obj.author)
        # return (request.user == obj) or request.user.is_admin
