from django.urls import include, re_path
from django.contrib import admin
from django.conf import settings

from controls.models import Element
from siteapp.model_mixins.tags import TagView, build_tag_urls

admin.autodiscover()

from django.views.decorators.csrf import csrf_exempt

import controls.views
from nlp import views

from siteapp.settings import *

urlpatterns = [

    re_path(r'^nlp_index$', views.index, name="nlp_index"),
    # re_path(r'^nlp_index$', views.component_library, name="component_library"),


# COPIED LINKS
    # Docs
    # re_path('doc/', include('django.contrib.admindocs.urls')),

    # re_path(r'^(?P<system_id>.*)/controls/selected/export/xacta/xlsx$', views.controls_selected_export_xacta_xslx, name="controls_selected"),

    # Catalogs
    # re_path(r'^$', views.catalogs),
    # re_path(r'^catalogs$', views.catalogs),
    # re_path(r'^catalogs/(?P<catalog_key>.*)/$', views.catalog),


]
