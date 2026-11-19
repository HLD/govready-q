from django.urls import include, re_path
from . import views

INTEGRATION_NAME = "jsonplaceholder"
urlpatterns = [

    re_path(r"^$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    re_path(r"^identify$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    re_path(r"^endpoint(?P<endpoint>.*)$", views.integration_endpoint,
        name=f'{INTEGRATION_NAME}_integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    re_path(r"^post_endpoint(?P<endpoint>.*)$", views.integration_endpoint_post,
        name=f'{INTEGRATION_NAME}_integration_endpoint'),
]
