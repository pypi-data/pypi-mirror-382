from rest_framework.permissions import BasePermission, SAFE_METHODS
from huscy.projects.services import is_project_coordinator, is_project_member_with_write_permission


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.method in SAFE_METHODS


class ChangeProjectPermission(BasePermission):
    def has_object_permission(self, request, view, project):
        if request.method in ['PATCH', 'PUT']:
            return any([
                request.user.has_perm('projects.change_project'),
                is_project_member_with_write_permission(project, request.user),
            ])
        return True


class CreateProjectPermission(BasePermission):
    pass


class DeleteProjectPermission(BasePermission):
    def has_object_permission(self, request, view, project):
        if request.method == 'DELETE':
            return any([
                request.user.has_perm('projects.delete_project'),
                request.user.has_perm('projects.delete_project', project),
            ])
        return True


class IsProjectCoordinator(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return is_project_coordinator(view.project, request.user)

    def has_object_permission(self, request, view, instance):
        if request.user.is_superuser:
            return True
        return is_project_coordinator(view.project, request.user)
