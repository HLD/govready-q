from django.urls import include, re_path
from django.contrib import admin
from django.conf import settings

from controls.models import Element
from siteapp.model_mixins.tags import TagView, build_tag_urls

admin.autodiscover()

from django.views.decorators.csrf import csrf_exempt

from controls import views

from siteapp.settings import *

urlpatterns = [
    # Docs
    re_path('doc/', include('django.contrib.admindocs.urls')),

    # Catalogs
    re_path(r'^catalogs$', views.catalogs),
    re_path(r'^catalogs$', views.catalogs),
    re_path(r'^catalogs/(?P<catalog_key>.*)/$', views.catalog),

    # Systems
    re_path(r'^(?P<system_id>.*)/controls/selected/export/xacta/xlsx$', views.controls_selected_export_xacta_xslx, name="controls_selected"),
    re_path(r'^(?P<system_id>.*)/controls/selected/aspen$', views.controls_selected_aspen, name="controls_selected_aspen"),
    re_path(r'^(?P<system_id>.*)/controls/selected$', views.controls_selected, name="controls_selected"),
    re_path(r'^(?P<system_id>.*)/controls/add$', views.system_controls_add, name="system_controls_add"),
    re_path(r'^(?P<system_id>.*)/controls/remove/(?P<element_control_id>.*)$',  views.system_control_remove, name="system_control_remove"),

    re_path(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)/compare$', views.editor_compare, name="control_compare"),
    re_path(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)$', views.editor, name="control_editor"),
    re_path(r'^editor_autocomplete/', views.EditorAutocomplete.as_view(), name="search_system_component"),
    re_path(r'^related_system_components/', views.RelatedComponentStatements.as_view(), name="related_system_components"),
    re_path(r'^(?P<system_id>.*)/components/add_system_component$', views.add_system_component, name="add_system_component"),
    re_path(r'^(?P<system_id>.*)/components/proposal_message$', views.proposal_message, name="proposal_message"),
    re_path(r'^(?P<system_id>.*)/components/remove_proposal/(?P<proposal_id>.*)$', views.system_proposal_remove, name="system_proposal_remove"),

    re_path(r'^(?P<system_id>.*)/components/editor_autocomplete$',  views.EditorAutocomplete.as_view(), name="editor_autocomplete"),
    re_path(r'^(?P<system_id>.)/profile/oscal/json', views.system_profile_oscal_json, name="profile_oscal_json"),
    re_path(r'^statement_history/(?P<smt_id>.*)/$', views.statement_history, name="statement_history"),
    re_path(r'^restore_to/(?P<smt_id>.*)/(?P<history_id>.*)/$', views.restore_to_history, name="restore_to"),

    re_path(r'^(?P<system_id>.*)/aspen/summary$', views.system_summary_aspen, name="system_summary"),
    re_path(r'^(?P<system_id>.*)/aspen/summary/fake$', views.system_summary_1_aspen, name="system_summary_1"),
    re_path(r'^(?P<system_id>.*)/aspen/integrations$', views.system_integrations_aspen, name="system_integrations"),

    re_path(r'^(?P<system_id>.*)/aspen/summary/poams$', views.system_poams_aspen, name="system_summary_poams"),

    re_path(r'^new', views.create_new_system, name="create_new_system"),
    re_path(r'^csv_system_template', views.system_csv_template, name="csv_system_template"),
    re_path(r'^xlsx_system_template', views.system_xlsx_template, name="xlsx_system_template"),
    re_path(r'^oscal_system_template', views.system_oscal_template, name="oscal_system_template"),

    # Systems Assessment Results
    re_path(r'^(?P<system_id>.*)/assessments$', views.system_assessment_results_list, name="system_assessment_results_list"),
    re_path(r'^(?P<system_id>.*)/assessments/new/wazuh$', views.new_system_assessment_result_wazuh, name="new_system_assessment_result_wazuh"),
    re_path(r'^(?P<system_id>.*)/assessment/new$', views.manage_system_assessment_result, name="new_system_assessment_result"),
    re_path(r'^(?P<system_id>.*)/sar/(?P<sar_id>.*)/view$', views.view_system_assessment_result_summary, name="view_system_assessment_result_summary"),
    re_path(r'^(?P<system_id>.*)/sar/(?P<sar_id>.*)/edit$', views.manage_system_assessment_result, name="manage_system_assessment_result"),
    re_path(r'^(?P<system_id>.*)/sar/(?P<sar_id>.*)/history$', views.system_assessment_result_history, name="system_assessment_result_history"),

    # Systems Inventory and Deployments
    re_path(r'^(?P<system_id>.*)/aspen/deployments$', views.system_deployments_aspen, name="system_deployments_aspen"),
    re_path(r'^(?P<system_id>.*)/deployments$', views.system_deployments, name="system_deployments"),
    re_path(r'^(?P<system_id>.*)/deployment/new$', views.manage_system_deployment, name="new_system_deployment"),
    re_path(r'^(?P<system_id>.*)/deployment/(?P<deployment_id>.*)/edit$', views.manage_system_deployment, name="manage_system_deployment"),
    re_path(r'^(?P<system_id>.*)/deployment/(?P<deployment_id>.*)/inventory$', views.system_deployment_inventory, name="system_deployment_inventory"),
    re_path(r'^(?P<system_id>.*)/deployment/(?P<deployment_id>.*)/history$', views.deployment_history, name="deployment_history"),

    # Statements
    re_path(r'^smt/_save/$', views.save_smt),
    re_path(r'^smt/_delete/$', views.delete_smt),
    re_path(r'^smt/_update_smt_prototype/$', views.update_smt_prototype),

    # System Components/Elements
    re_path(r'^(?P<system_id>.*)/aspen/components/selected$', views.SelectedComponentsListAspen.as_view(), name="components_selected_aspen"),
    re_path(r'^(?P<system_id>.*)/components/selected$', views.SelectedComponentsList.as_view(), name="components_selected"),
    re_path(r'^(?P<system_id>.*)/components/selected/export/opencontrol$', views.export_system_opencontrol, name="export_system_opencontrol"),
    re_path(r'^(?P<system_id>.*)/component/(?P<element_id>.*)/download/oscal/json$',
        views.system_element_download_oscal_json,
        name="system_element_download_oscal_json"),
    re_path(r'^(?P<system_id>.*)/component/(?P<element_id>.*)/_remove$', views.system_element_remove, name="system_element_remove"),
    re_path(r'^(?P<system_id>.*)/component/(?P<element_id>.*)/(?P<catalog_key>.*)/(?P<control_id>.*)$', views.system_element_control, name="system_element_control"),
    re_path(r'^(?P<system_id>.*)/components/(?P<element_id>.*)/proposal_message$', views.proposal_message, name="proposal_message"),
    re_path(r'^(?P<system_id>.*)/component/(?P<element_id>.*)$', views.system_element, name="system_element"),
    re_path(r'^(?P<system_id>.*)/controls/updated$', views.controls_updated, name="controls_updated"),
    re_path(r'^system_import$', views.system_import, name="system_import"),
    re_path(r'^revert_system_import$', views.revert_system_import, name="revert_system_import"),

    # Component Library
    re_path(r'^components$', views.component_library, name="component_library"),
    re_path(r'^components/compare$', views.compare_components, name="compare_components"),
    re_path(r'^components/new$', views.new_element, name="new_element"),
    re_path(r'^components/(?P<element_id>.*)/edit_component_state$',  views.edit_component_state, name="edit_component_state"),
    re_path(r'^components/(?P<element_id>.*)/edit_component_type$',  views.edit_component_type, name="edit_component_type"),
    re_path(r'^components/(?P<element_id>.*)/_copy$', views.component_library_component_copy, name="component_library_component_copy"),
    re_path(r'^components/(?P<element_id>.*)$', views.component_library_component, name="component_library_component"),
    re_path(r'^import_component$', views.import_component, name="import_component"),
    re_path(r'^import_records$', views.import_records, name="import_records"),
    re_path(r'^import_records/(?P<import_record_id>.*)/details$', views.import_record_details, name="import_record_details"),
    re_path(r'^import_records/(?P<import_record_id>.*)/delete_confirm$', views.confirm_import_record_delete, name="confirm_import_record_delete"),
    re_path(r'^import_records/(?P<import_record_id>.*)/delete$', views.import_record_delete, name="import_record_delete"),

    # Elements
    re_path(r'^elements/(\d+)/__edit$', views.edit_element, name="edit_element"),
    re_path(r'^elements/(\d+)/__edit_access$', views.edit_element_access_management, name="edit_element_access_management"),
    *build_tag_urls(r"^elements/(\d+)/", model=Element),  # Tag Urls

    # Controls
    re_path(r'^catalogs/(?P<catalog_key>.*)/group/(?P<g_id>.*)', views.group, name="control_group"),
    re_path(r'^catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)', views.control, name="control_info"),
    re_path(r'^api/controlsselect/', views.api_controls_select, name="api_controls_select"),

    # System Security plan
    re_path(r'^(?P<system_id>.*)/export/oscal', views.OSCAL_ssp_export, name="ssp_export_oscal"),

    # Baselines
    re_path(r'^(?P<system_id>.*)/controls/baseline/(?P<catalog_key>.*)/(?P<baseline_name>.*)/_assign$', views.assign_baseline, name="assign_baseline"),

    # Poams
    re_path(r'^(?P<system_id>.*)/aspen/poams$', views.system_poams_aspen, name="system_poams_aspen"),
    
    re_path(r'^(?P<system_id>.*)/poams$', views.poams_list, name="poams_list"),
    re_path(r'^(?P<system_id>.*)/poams/new$', views.new_poam, name="new_poam"),
    re_path(r'^(?P<system_id>.*)/poams/(?P<poam_id>.*)/edit$', views.edit_poam, name="edit_poam"),
    re_path(r'^(?P<system_id>.*)/poams/export/csv$', views.poam_export_csv, name="poam_export_csv"),
    re_path(r'^(?P<system_id>.*)/poams/export/xlsx$', views.poam_export_xlsx, name="poam_export_xlsx"),

    # Project
    re_path(r'^(?P<project_id>.*)/import', views.project_import, name="project_import"),
    re_path(r'^(?P<project_id>.*)/export', views.project_export, name="project_export"),
]
