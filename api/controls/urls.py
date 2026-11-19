from django.urls import re_path
from django.urls import include
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter
from api.controls.views.element import ElementViewSet, ElementWithPermissionsViewSet
from api.controls.views.system import SystemViewSet, SystemControlsViewSet, SystemAssessmentViewSet, SystemPoamViewSet, SystemPoamSpreadsheetViewSet

router = routers.DefaultRouter()
router.register(r'elements', ElementViewSet)
router.register(r'element_permissions', ElementWithPermissionsViewSet, basename='element_permissions')
router.register(r'systems', SystemViewSet)

systems_router = NestedSimpleRouter(router, r'systems', lookup='systems')
systems_router.register(r'controls', SystemControlsViewSet, basename='systems-controls')
systems_router.register(r'assessments', SystemAssessmentViewSet, basename='systems-assessments')
systems_router.register(r'poams', SystemPoamViewSet, basename='systems-poams')
systems_router.register(r'spreadsheet-poams', SystemPoamSpreadsheetViewSet, basename='systems-spreadsheet-poams')
urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^', include(systems_router.urls))
]
