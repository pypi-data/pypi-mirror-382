from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from huscy.projects import views


router = DefaultRouter()
router.register('projects', views.ProjectViewSet, basename='project')
router.register('researchunits', views.ResearchUnitViewSet)

project_router = NestedDefaultRouter(router, 'projects', lookup='project')
project_router.register('memberships', views.MembershipViewSet, basename='membership')

urlpatterns = [
    path('api/', include(router.urls + project_router.urls)),
]
