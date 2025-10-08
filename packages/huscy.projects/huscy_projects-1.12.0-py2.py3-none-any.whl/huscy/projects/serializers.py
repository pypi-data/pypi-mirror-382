from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from huscy.projects.models import Membership, Project, ResearchUnit
from huscy.projects.services import (
    create_membership,
    create_project,
    set_principal_investigator,
    update_membership,
    update_project,
)


class ResearchUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchUnit
        fields = (
            'id',
            'code',
            'name',
            'principal_investigator',
        )


class PrincipalInvestigatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = 'principal_investigator',

    def update(self, project, validated_data):
        principal_investigator = validated_data.get('principal_investigator')
        try:
            return set_principal_investigator(project=project, user=principal_investigator)
        except ValueError as e:
            raise ValidationError({'detail': e})


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = (
            'id',
            'description',
            'local_id',
            'local_id_name',
            'participating',
            'principal_investigator',
            'principal_investigator_name',
            'research_unit',
            'research_unit_name',
            'title',
        )
        extra_args = {
            'description': {'required': False},
            'local_id': {'required': False},
            'title': {'required': False},
        }
        read_only_fields = 'principal_investigator', 'research_unit'

    participating = serializers.SerializerMethodField()
    principal_investigator_name = serializers.CharField(
        source='principal_investigator.get_full_name', read_only=True,
    )
    research_unit_name = serializers.CharField(source='research_unit.name', read_only=True)

    # default=None is used as required=False does not work together with the unique_together
    # constraint, however this defaut=None is a workaround, see:
    # https://github.com/encode/django-rest-framework/issues/4456
    local_id = serializers.IntegerField(min_value=1, default=None)

    def get_participating(self, project):
        user = self.context['request'].user
        return (project.principal_investigator == user or
                project.membership_set.filter(user=user).exists())

    def update(self, project, validated_data):
        try:
            return update_project(project=project, **validated_data)
        except IntegrityError:
            raise ValidationError({'local_id': ['Local ID already exists.']})


class CreateProjectSerializer(ProjectSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Project
        fields = (
            'id',
            'creator',
            'description',
            'local_id',
            'local_id_name',
            'participating',
            'principal_investigator',
            'principal_investigator_name',
            'research_unit',
            'research_unit_name',
            'title',
        )

    def create(self, validated_data):
        return create_project(**validated_data)


class MembershipSerializer(serializers.ModelSerializer):
    has_write_permission = serializers.BooleanField()
    username = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Membership
        fields = (
            'id',
            'has_write_permission',
            'is_coordinator',
            'project',
            'user',
            'username',
        )
        read_only_fields = 'project',

    def create(self, validated_data):
        return create_membership(**validated_data)

    def update(self, membership, validated_data):
        return update_membership(membership, validated_data.get('is_coordinator'),
                                 validated_data.get('has_write_permission'))
