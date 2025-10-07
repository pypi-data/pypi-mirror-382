from rest_framework.permissions import BasePermission, SAFE_METHODS
from huscy.projects.models import Membership


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.method in SAFE_METHODS


class BaseProjectPermission(BasePermission):
    def _is_project_coordinator(self, project, user):
        return Membership.objects.filter(project=project, user=user, is_coordinator=True).exists()


class ChangeProjectPermission(BaseProjectPermission):
    def has_object_permission(self, request, view, project):
        if request.method in ['PATCH', 'PUT']:
            return any([
                request.user.has_perm('projects.change_project'),
                request.user.has_perm('projects.change_project', project),
                self._is_project_coordinator(project, request.user),
            ])
        return True


class CreateProjectPermission(BaseProjectPermission):
    pass


class DeleteProjectPermission(BaseProjectPermission):
    def has_object_permission(self, request, view, project):
        if request.method == 'DELETE':
            return any([
                request.user.has_perm('projects.delete_project'),
                request.user.has_perm('projects.delete_project', project),
            ])
        return True


class IsProjectCoordinator(BaseProjectPermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return self._is_project_coordinator(view.project, request.user)

    def has_object_permission(self, request, view, instance):
        if request.user.is_superuser:
            return True
        return self._is_project_coordinator(view.project, request.user)
