from django.urls import re_path
from django.urls import include

from api.base.urls import get_swagger_urls

urlpatterns = [
    re_path(r'^', include('api.controls.urls')),
    re_path(r'^', include('api.discussion.urls')),
    re_path(r'^', include('api.guidedmodules.urls')),
    re_path(r'^', include('api.siteapp.urls')),
] + get_swagger_urls()
