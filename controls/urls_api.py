from django.urls import include, re_path

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

# import controls.views
from . import views_api

urlpatterns = [
    re_path(r'^(?P<system_id>.*)/assessment/new$', views_api.manage_system_assessment_result_api, name="new_system_assessment_result_api"),
]
