from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from rest_framework import routers
from rest_framework import serializers
from siteapp.views import UserViewSet
from siteapp.views import ProjectViewSet

from .model_mixins.tags import build_tag_urls
from .models import Project

admin.autodiscover()

import siteapp.views as views
import dbstorage.views
import siteapp.views_landing as views_landing
import siteapp.views_health as views_health
import siteapp.views_management as views_management
from .good_settings_helpers import signup_wrapper
from .settings import *

urlpatterns = [
    re_path(r"^warningmessage/$", views.banner, name="banner"),
    re_path(r"^(?![\s\S])$", views.home_user, name="home_user"),
    re_path(r"^login$", views.homepage, name="homepage"),
    re_path(r"^(privacy|terms-of-service|love-assessments)$", views.shared_static_pages, name="privacy_terms_love"),

    re_path(r'^api/v1/projects/(?P<project_id>\d+)/answers$', views_landing.project_api),
    re_path(r'^media/users/(\d+)/photo/(\w+)', views_landing.user_profile_photo),

    # incoming email hook for responses to notifications
    re_path(r'^notification_reply_email_hook$', views_landing.notification_reply_email_hook, name='notifications'),

    # NLP
    re_path(r"^nlp/", include("nlp.urls")),

    # Django rest framework
    # path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Django admin site
    re_path(r'^admin/', admin.site.urls),
    # dbstorage's own urls.py uses django.conf.urls.url(), removed in Django 4.0, so route its view directly.
    re_path(r'^media/(.*)', dbstorage.views.get_file_content_view, name='get_file_content_view'),
    # apps
    re_path(r"^tasks/", include("guidedmodules.urls")),
    re_path(r"^discussion/", include("discussion.urls")),

    # app store
    re_path(r'^store$', views.apps_catalog, name="store"),
    re_path(r'^store/app/(?P<appversion_id>.*)/modules$', views.apps_catalog_item_modules, name='apps_catalog_item_modules'),
    # re_path(r'^store/app/(?P<appversion_id>.*)/clone$', views.apps_catalog_item_clone, name='apps_catalog_item_clone'),
    re_path(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)/zip$', views.apps_catalog_item_zip),
    re_path(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

    # app store
    re_path(r'^library$', views.apps_catalog),
    re_path(r'^library/(?P<source_slug>.*)/(?P<app_name>.*)/zip$', views.apps_catalog_item_zip),
    re_path(r'^library/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

    # profile
    re_path(r'account/settings$', views.account_settings, name="account_settings"),


    # projects
    re_path(r"^projects$", views.ProjectList.as_view(), name="projects"),
    re_path(r"^projects/lifecycle$", views.project_list_lifecycle, name="projects_lifecycle"),
    re_path(r'^projects/(?P<project_id>.*)/__edit$', views.project_edit, name="edit_project"),
    re_path(r'^projects/(?P<project_id>.*)/__edit_security_obj$', views.project_security_objs_edit, name="edit_project_security_objs"),
    re_path(r'^projects/(\d+)/__delete$', views.delete_project, name="delete_project"),
    re_path(r'^projects/(\d+)/__admins$', views.make_revoke_project_admin, name="make_revoke_project_admin"),
    re_path(r'^projects/(\d+)/__export$', views.export_project_questionnaire, name="export_project_questionnaire"),
    re_path(r'^projects/(\d+)/__import$', views.import_project_questionnaire, name="import_project_questionnaire"),
    re_path(r'^projects/(\d+)/__upgrade$', views.upgrade_project, name="upgrade_project"),
    re_path(r'^projects/(\d+)/__move$', views.move_project, name="move_project"),
    *build_tag_urls(r"^projects/(\d+)/", model=Project),  # Tag Urls
    re_path(r'^projects/(\d+)/assets/(\d+)/__update$', views.update_project_asset,
        name="update_project_assets"),
    re_path(r'^projects/(\d+)/$', views.project, name="view_project_id"),
    re_path(r'^projects/(\d+)/(?:[\w\-]+)()$', views.project, name="view_project"), # must be last because regex matches some previous URLs
    
    re_path(r"^system/", include("controls.urls")),
    re_path(r'^systems/(\d+)/$', views.project, name="view_project_id_2"),
    re_path(r'^systems/(\d+)/(?:[\w\-]+)()$', views.project, name="view_project_2"), # must be last because regex matches some previous URLs
    

    re_path(r'^projects/(\d+)/(?:[\w\-]+)(/settings)$', views.project_settings, name="project_settings"),
    re_path(r'^projects/(\d+)/(?:[\w\-]+)(/startapps)$', views.project_start_apps),
    # must be last because regex matches some previous URLs
    re_path(r'^projects/(\d+)/(?:[\w\-]+)(/list)$', views.project_list_all_answers),
    # must be last because regex matches some previous URLs
    re_path(r'^projects/(\d+)/(?:[\w\-]+)(/outputs)$', views.project_outputs),
    # must be last because regex matches some previous URLs
    re_path(r'^projects/(\d+)/(?:[\w\-]+)(/api)$', views.project_api),
    # must be last because regex matches some previous URLs

    # Controls and Systems
    re_path(r"^systems$", views.ProjectList.as_view(), name="systems"),
    re_path(r"^systems/$", views.ProjectList.as_view(), name="systems_2"),
    re_path(r"^system$", views.ProjectList.as_view(), name="systems_3"),
    re_path(r"^system/$", views.ProjectList.as_view(), name="systems_4"),
    
    re_path(r"^systems/", include("controls.urls")),
    re_path(r"^api/v1/systems/", include("controls.urls_api")),

    re_path(r"^controls$", include("controls.urls")),
    re_path(r"^controls/", include("controls.urls")),

    # portfolios
    re_path(r'^portfolios$', views.portfolio_list, name="list_portfolios"),
    re_path(r'^portfolios/new$', views.new_portfolio, name='new_portfolio'),
    re_path(r'^portfolios/(?P<pk>.*)/delete$', views.delete_portfolio, name="delete_portfolio"),
    re_path(r'^portfolios/(?P<pk>.*)/edit$', views.edit_portfolio, name="edit_portfolio"),
    re_path(r'^portfolios/(?P<pk>.*)/projects$', views.portfolio_projects, name="portfolio_projects"),
    re_path(r'^portfolio/update_permissions', views.update_permissions, name="update_permissions"),

    # org groups
    re_path(r'^groups$', views_landing.org_groups),
    re_path(r'^groups/new$', views_landing.new_org_group),
    re_path(r"^(?P<org_slug>.*)/projects$", views_landing.org_group_projects, name='org_projects'),

    # api
    re_path(r'^api-keys$', views.show_api_keys, name="show_api_keys"),

    # invitations
    re_path(r'^invitation/_send$', views.send_invitation, name="send_invitation"),
    re_path(r'^invitation/_cancel$', views.cancel_invitation, name="cancel_invitation"),
    re_path(r'^invitation/accept/(?P<code>.+)$', views.accept_invitation, name="accept_invitation"),

    # support
    re_path(r'^support$', views.support, name="support"),

    # administration
    re_path(r'^settings$', views.organization_settings),
    re_path(r'^settings/_save$', views.organization_settings_save),

    # health
    re_path(r'^health/$', views_health.index),
    re_path(r'^health/check-system$', views_health.check_system),
    re_path(r'^health/check-vendor-resources$', views_health.check_vendor_resources),
    re_path(r'^health/list-vendor-resources$', views_health.list_vendor_resources),
    re_path(r'^health/load-base/(?P<args>.*)$', views_health.load_base),
    re_path(r'^health/request-headers$', views_health.request_headers),
    re_path(r'^health/request$', views_health.request),
    re_path(r'^health/debug$', views.debug, name="debug"),

    # tags
    re_path(r'^tags/_save$', views.create_tag),
    re_path(r'^tags/(\d+)/_delete$', views.delete_tag),
    re_path(r'^tags/$', views.list_tags),

    # Session
    re_path(r'session_security/', include('session_security.urls')),

    # management commands
    re_path(r'^management/$', views_management.index),
    re_path(r'^management/is_superuser$', views_management.is_superuser),
    re_path(r'^management/listcomponents$', views_management.listcomponents),
]

urlpatterns += [re_path(r'^api/v2/', include('api.urls'))]
urlpatterns += [re_path(r'^integrations/', include('integrations.urls'))]
urlpatterns += [re_path(r'^workflow/', include('workflow.urls'))]

if settings.OKTA_CONFIG or settings.OIDC_CONFIG:
    urlpatterns += [
        path('oidc/', include('mozilla_django_oidc.urls')),
        re_path(r'^accounts/logout/$', views.logged_out, name="logged_out"),
        re_path(r'^accounts/login/$', RedirectView.as_view(url='/oidc/authenticate', permanent=False), name='login2')
    ]

if 'django.contrib.auth.backends.ModelBackend' in settings.AUTHENTICATION_BACKENDS:
    # If username/pwd logins are enabled, add the login pages.
    urlpatterns += [
        # auth
        # next line overrides signup with our own view so we can monitor signup attempts, can comment out to go back to allauth's functionality
        re_path(r'^accounts/signup/', signup_wrapper, name="account_signup"),
        # Disregard re-routing login to home page. Instead, use custom templates to style aullauth templates
        # Necessary to keep existing routing in place to support links from invitation acceptance page
        # and proper routing of "NEXT" url to project after after accepting invitation
        # login button will redirect to the homepage with a login form
        re_path(r'^accounts/', include('allauth.urls')),
    ]

import notifications.urls

urlpatterns += [
    re_path('^user/notifications/', include(notifications.urls, namespace='notifications')),
    re_path('^_mark_notifications_as_read', views.mark_notifications_as_read),
]

# Enterprise Single Sign On
# if SSO Proxy enabled, add-in route to `/accounts/logout/` which comes from Django's account
# module but is not present from Django when SSO Proxy enabled
if environment.get("trust-user-authentication-headers"):
    print("settings.PROXY_AUTHENTICATION_USER_HEADER enabled. Catching route accounts/logout/")

    urlpatterns += [
        re_path(r'^accounts/logout/$',
                views.exedev_logout if getattr(settings, 'EXEDEV_AUTH', None) else views.sso_logout,
                name="sso-logout")
    ]
