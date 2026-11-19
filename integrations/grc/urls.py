from django.urls import include, re_path
from . import views

INTEGRATION_NAME = 'grc'

urlpatterns = [

    re_path(r"^$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    re_path(r"^identify$", views.integration_identify, name=f'{INTEGRATION_NAME}_integration_identify'),
    re_path(r"^endpoint(?P<endpoint>.*)$", views.integration_endpoint,
        name=f'{INTEGRATION_NAME}_integration_endpoint'),  # Ex: /integrations/csam/endpoint/system/111
    re_path(r"^post_endpoint(?P<endpoint>.*)$", views.integration_endpoint_post,
        name=f'{INTEGRATION_NAME}_integration_endpoint'),

    re_path(r"^get_system_info_test/(?P<system_id>.*)$", views.get_system_info, name=f'{INTEGRATION_NAME}_get_system_info_test'),
    re_path(r"^update_system_description_test/(?P<system_id>.*)$", views.update_system_description_test,
        name=f'{INTEGRATION_NAME}_update_system_description_test'),
    re_path(r"^update_system_description$", views.update_system_description,
        name=f'{INTEGRATION_NAME}_update_system_description'),

    re_path(r"^get_multiple_system_info/(?P<system_id_list>.*)$", views.get_multiple_system_info, name=f'{INTEGRATION_NAME}_get_multiple_system_info'),

    re_path(r"^local/system/(?P<system_id>.*)$", views.get_paired_remote_system_info_using_local_system_id, name=f'{INTEGRATION_NAME}_csam_system_info'),

    re_path(r"^create_system_from_remote/$", views.create_system_from_remote, name=f'{INTEGRATION_NAME}_create_system_from_remote'),
    re_path(r"^create_system_from_remote/(?P<remote_system_id>.*)$", views.create_system_from_remote, name=f'{INTEGRATION_NAME}_create_system_from_remote'),

]
