from django.core.exceptions import PermissionDenied
from django.db.models import Q

from lbworkflow import settings
from lbworkflow.models import Task

from .helper import get_base_wf_permit_query_param


class BasePermission:
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True


class AllowAny(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """
    pass


class PermissionMixin:
    permission_classes = settings.perform_import(
        settings.DEFAULT_PERMISSION_CLASSES
    )

    def permission_denied(self, request, message=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        raise PermissionDenied()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.permission_classes]

    def check_all_permissions(self, request, obj):
        """
        call check_permissions && check_object_permissions
        """
        self.check_permissions(request)
        self.check_object_permissions(request, obj)

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )

    def check_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )


class DefaultEditWorkFlowPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        instance = obj.pinstance
        user = request.user
        if instance.is_wf_admin(user):
            return True
        if instance.cur_node.status in ['draft', 'given up', 'rejected'] and instance.created_by == user:
            return True
        task = Task.objects.filter(
            Q(user=user) | Q(agent_user=user),
            instance=instance, status='in progress').first()
        if instance.cur_node.can_edit and task:
            return True
        return False


class DefaultDetailWorkFlowPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if not obj:
            return False
        qs = obj.__class__.objects.all()
        q_param = get_base_wf_permit_query_param(user)
        qs = qs.filter(q_param)
        return qs.filter(pk=obj.pk).exists()
