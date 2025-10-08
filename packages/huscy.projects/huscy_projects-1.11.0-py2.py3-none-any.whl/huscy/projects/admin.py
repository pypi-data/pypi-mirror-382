from django.contrib import admin
from reversion.admin import VersionAdmin

from huscy.projects import models
from huscy.projects.services import create_project


@admin.register(models.ResearchUnit)
class ResearchUnitAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = 'name', 'code', 'principal_investigator'
    search_fields = (
        'name',
        'principal_investigator__first_name',
        'principal_investigator__last_name',
    )


@admin.register(models.Project)
class ProjectAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = 'id', 'local_id_name', 'title', 'principal_investigator'
    search_fields = (
        'principal_investigator__first_name',
        'principal_investigator__last_name',
        'title',
    )

    def save_model(self, request, project, form, change):
        if change:
            super().save_model(request, project, form, change)
        else:
            create_project(project.title, project.research_unit, project.principal_investigator,
                           creator=request.user, local_id=project.local_id,
                           description=project.description)


@admin.register(models.Membership)
class MembershipAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = 'id', '_project', 'user', 'is_coordinator', 'has_write_permission'
    list_filter = 'is_coordinator',
    search_fields = 'project__title', 'user__first_name', 'user__last_name'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def _project(self, membership):
        project = membership.project
        return f'{project.id} ({project.local_id_name} {project.title})'
