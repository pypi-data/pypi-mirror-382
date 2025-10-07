from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_default_for_research_unit_code():
    return uuid4().hex


class ResearchUnit(models.Model):
    name = models.CharField(_('Name'), max_length=128, unique=True)
    code = models.CharField(_('Code'), max_length=32, unique=True, blank=True,
                            default=get_default_for_research_unit_code)
    principal_investigator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                               verbose_name=_('Principal investigator'))

    local_id_start_value = models.PositiveIntegerField(_('Local ID start value'),
                                                       default=1)

    def __str__(self):
        return f'{self.name} ({self.principal_investigator.get_full_name()})'

    class Meta:
        ordering = 'name',
        verbose_name = _('Research unit')
        verbose_name_plural = _('Research units')


class Project(models.Model):
    research_unit = models.ForeignKey(ResearchUnit, on_delete=models.PROTECT,
                                      verbose_name=_('Research unit'))
    local_id = models.PositiveIntegerField(_('Local ID'))

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, default='')

    principal_investigator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                               related_name='+',
                                               verbose_name=_('Principal investigator'))

    @property
    def local_id_name(self):
        return f'{self.research_unit.code}-{self.local_id}'

    class Meta:
        ordering = '-id',
        unique_together = ('local_id', 'research_unit')
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name=_('User'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('Project'))
    is_coordinator = models.BooleanField(_('Is coordinator'), default=False)

    @property
    def has_write_permission(self):
        return self.user.has_perm('change_project', self.project)

    def __str__(self):
        return f'{self.user.get_full_name()} is member in project {self.project.title}'

    class Meta:
        ordering = 'project', 'user'
        unique_together = 'user', 'project'
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')
