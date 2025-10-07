from itertools import count, filterfalse

from django.db.models import Q
from django.db.transaction import atomic
from guardian.shortcuts import assign_perm, remove_perm

from huscy.projects.models import Membership, Project, ResearchUnit


@atomic
def create_membership(project, user, is_coordinator=False, has_write_permission=False):
    assign_perm('view_project', user, project)
    if is_coordinator or has_write_permission:
        assign_perm('change_project', user, project)
    return Membership.objects.create(
        project=project,
        user=user,
        is_coordinator=is_coordinator,
    )


@atomic
def create_project(title, research_unit, principal_investigator, creator,
                   local_id=None, description=''):
    if local_id is None:
        local_id = _get_next_local_id(research_unit)

    project = Project.objects.create(
        description=description,
        local_id=local_id,
        principal_investigator=principal_investigator,
        research_unit=research_unit,
        title=title,
    )

    create_membership(project, principal_investigator, is_coordinator=True)
    if principal_investigator != creator:
        create_membership(project, creator, is_coordinator=True)

    return project


def _get_next_local_id(research_unit):
    taken_values = (Project.objects.filter(research_unit=research_unit)
                                   .values_list('local_id', flat=True))
    return next(filterfalse(lambda x: x in set(taken_values),
                            count(research_unit.local_id_start_value)))


@atomic
def delete_membership(membership):
    remove_perm('view_project', membership.user, membership.project)
    remove_perm('change_project', membership.user, membership.project)
    membership.delete()


@atomic
def delete_project(project):
    map(delete_membership, project.membership_set.all())
    project.delete()


def get_memberships(project):
    return Membership.objects.filter(project=project)


def get_participating_projects(user):
    return (Project.objects
                   .filter(Q(principal_investigator=user) | Q(membership__user=user))
                   .distinct())


def get_projects():
    return Project.objects.all()


def get_research_units():
    return ResearchUnit.objects.all()


def set_principal_investigator(project, user):
    if not Membership.objects.filter(project=project, user=user, is_coordinator=True).exists():
        raise ValueError('Only project members who are coordinators can become '
                         'principal investigators.')

    project.principal_investigator = user
    project.save(update_fields=['principal_investigator'])
    return project


def update_membership(membership, is_coordinator, has_write_permission):
    if is_coordinator or has_write_permission:
        assign_perm('change_project', membership.user, membership.project)
    else:
        remove_perm('change_project', membership.user, membership.project)
    membership.is_coordinator = is_coordinator
    membership.save()
    return membership


def update_project(project, local_id=None, title=None, description=None):
    update_fields = []
    if local_id is not None:
        project.local_id = local_id
        update_fields.append('local_id')
    if title is not None:
        project.title = title
        update_fields.append('title')
    if description is not None:
        project.description = description
        update_fields.append('description')
    project.save(update_fields=update_fields)
    return project
