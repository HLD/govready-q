from django.urls import include, re_path

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [

    # multi-question authoring tool
    re_path(r'^module/(\d+)/questions$', guidedmodules.views.show_module_questions, name="show_module_questions"),
    re_path(r'^_authoring_tool/edit-question2$', guidedmodules.views.authoring_edit_question2),
    re_path(r'^module/(\d+)/artifact/new$', guidedmodules.views.add_module_artifact, name="add_module_artifact"),
    re_path(r'^module/(\d+)/artifact/([\w_-]+)$', guidedmodules.views.show_module_artifact, name="show_module_artifact"),
    re_path(r'^_authoring_tool/edit-artifact$', guidedmodules.views.authoring_edit_artifact, name="authoring_edit_artifact"),

    # question management urls
    re_path(r'^(\d+)/([\w_-]+)(/_save)()$', guidedmodules.views.save_answer),
    re_path(r'^(\d+)/([\w_-]+)(/question/)([\w_-]+)$', guidedmodules.views.show_question),
    re_path(r'^(\d+)/([\w_-]+)(/question/)([\w_-]+)/history/(\d+)/media$', guidedmodules.views.download_answer_file),
    re_path(r'^(\d+)/([\w_-]+)(/finished)()$', guidedmodules.views.task_finished),
    re_path(r'^(\d+)/([\w_-]+)/media/(.*)$', guidedmodules.views.download_module_asset),
    re_path(r'^(\d+)/([\w_-]+)/(download/document)()/(.*)/(.*)$', guidedmodules.views.download_module_output),
    re_path(r'^(\d+)/([\w_-]+)()()$', guidedmodules.views.next_question),
    re_path(r'^start$', guidedmodules.views.new_task),
    re_path(r'^_delete_task$', guidedmodules.views.delete_task, name="delete_task"),
    re_path(r'^_get_task_timetamp$', guidedmodules.views.get_task_timetamp, name="task_get_timestamp"),
    re_path(r'^_instrumentation_record_interaction$', guidedmodules.views.instrumentation_record_interaction, name="task_instrumentation_record_interaction"),
    re_path(r'^_start_discussion', guidedmodules.views.start_a_discussion, name="start_a_discussion"),
    re_path(r'^analytics$', guidedmodules.views.analytics, name="guidedmodules_analytics"),
    re_path(r'^_authoring_tool/new-question$', guidedmodules.views.authoring_new_question),
    re_path(r'^_authoring_tool/new-question2$', guidedmodules.views.authoring_new_question2),
    re_path(r'^_authoring_tool/edit-module$', guidedmodules.views.authoring_edit_module),
    re_path(r'^_authoring_tool/create-app-project$', guidedmodules.views.authoring_create_q),
    re_path(r'^_authoring_tool/import-appsource$', guidedmodules.views.authoring_import_appsource),
    re_path(r'^_authoring_tool/edit-appversion$', guidedmodules.views.authoring_edit_appversion, name="authoring_edit_appversion"),
    re_path(r'^_upgrade-app$', guidedmodules.views.upgrade_app),
    re_path(r'^_refresh-output-doc$', guidedmodules.views.refresh_output_doc),
]

