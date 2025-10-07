import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from reversion import set_comment
from reversion.views import RevisionMixin

from huscy.projects import serializers, services
from huscy.projects.models import Project
from huscy.projects.permissions import (
    ChangeProjectPermission,
    CreateProjectPermission,
    DeleteProjectPermission,
    IsProjectCoordinator,
    ReadOnly,
)

logger = logging.getLogger('projects')


class MembershipViewSet(RevisionMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.MembershipSerializer
    permission_classes = (IsAuthenticated, IsProjectCoordinator | ReadOnly)

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_memberships(self.project)

    def perform_create(self, serializer):
        membership = serializer.save(project=self.project)
        set_comment(f'Created membership <ID-{membership.id}> for project <ID-{self.project.id}>')

        logger.info('Membership created by user %s for project "%s" and member %s',
                    self.request.user.username, membership.project.title,
                    membership.user.get_full_name())

    def perform_destroy(self, membership):
        services.delete_membership(membership)
        set_comment(f'Deleted membership <ID-{membership.id}>')

        logger.info('Membership deleted by user %s for project "%s" and member %s',
                    self.request.user.username, membership.project.title,
                    membership.user.get_full_name())

    def perform_update(self, serializer):
        membership = serializer.save()
        set_comment(f'Updated membership <ID-{membership.id}>')

        logger.info('Membership updated by user %s for project "%s" and member %s',
                    self.request.user.username, membership.project.title,
                    membership.user.get_full_name())


class ViewProjectFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        if user.has_perm('projects.view_project'):
            return queryset
        return queryset.filter(Q(principal_investigator=user) | Q(membership__user=user))


class ProjectViewSet(RevisionMixin, viewsets.ModelViewSet):
    filter_backends = ViewProjectFilter,
    permission_classes = (IsAuthenticated, ChangeProjectPermission, CreateProjectPermission,
                          DeleteProjectPermission)
    queryset = services.get_projects()

    def initial(self, request, *args, **kwargs):
        if self.action == 'principalinvestigator':
            self.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        super().initial(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateProjectSerializer
        return serializers.ProjectSerializer

    def perform_create(self, serializer):
        project = serializer.save()
        set_comment(f'Created project <ID-{project.id}>')

        logger.info('Project created by user %s with title "%s"',
                    self.request.user.username, project.title)

    def perform_destroy(self, project):
        services.delete_project(project)
        set_comment(f'Deleted project <ID-{project.id}>')

        logger.info('Project deleted by user %s with title "%s"',
                    self.request.user.username, project.title)

    def perform_update(self, serializer):
        project = serializer.save()
        set_comment(f'Updated project <ID-{project.id}>')

        logger.info('Project updated by user %s with title "%s"',
                    self.request.user.username, project.title)

    @action(detail=True, methods=['PUT'],
            permission_classes=[IsAuthenticated, IsProjectCoordinator])
    def principalinvestigator(self, request, pk):
        serializer = serializers.PrincipalInvestigatorSerializer(instance=self.get_object(),
                                                                 data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()

        set_comment(f'Changed principal investigator for project <ID-{project.id}>')
        return Response(serializers.ProjectSerializer(project, context=dict(request=request)).data)


class ResearchUnitViewSet(RevisionMixin, viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissions | ReadOnly, )
    queryset = services.get_research_units()
    serializer_class = serializers.ResearchUnitSerializer

    def perform_create(self, serializer):
        research_unit = serializer.save()
        set_comment(f'Created research unit <ID-{research_unit.id}>')

    def perform_destroy(self, research_unit):
        research_unit.delete()
        set_comment(f'Deleted research unit <ID-{research_unit.id}>')

    def perform_update(self, serializer):
        research_unit = serializer.save()
        set_comment(f'Updated research unit <ID-{research_unit.id}>')
