from rest_framework import permissions


class IsOrderOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.customer_id == request.user.id
