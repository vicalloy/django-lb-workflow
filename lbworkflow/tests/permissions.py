from lbworkflow.views.permissions import BasePermission


class TestPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.username == "hr":
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.username == "tom":
            return False
        return True
