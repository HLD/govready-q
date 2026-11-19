from django.urls import include, re_path

from django.contrib import admin
admin.autodiscover()

import workflow.views as views

urlpatterns = [
    # re_path(r'^_discussion_comment_draft', views.update_discussion_comment_draft, name="discussion-comment-draft"),
    # re_path(r'^_discussion_comment_submit', views.submit_discussion_comment, name="discussion-comment-submit"),
    re_path(r'^(?P<workflowinstance_id>.*)/set_workflowinstance_feature_completed', views.set_workflowinstance_feature_completed, name="set_workflowinstance_feature_completed"),

    re_path(r'^recipes/all$', views.workflowrecipes_all, name="workflowrecipes_all"),
    re_path(r'^recipes/manage$', views.manage_recipe, name='manage_recipe'),
    re_path(r'^recipes/(?P<pk>.*)/edit$', views.edit_recipe, name="edit_recipe"),
    re_path(r'^recipes/(?P<pk>.*)/delete$', views.delete_recipe, name="delete_recipe"),
    re_path(r'^recipes/(?P<pk>.*)/duplicate$', views.duplicate_recipe, name="duplicate_recipe"),
    re_path(r'^recipes/(?P<pk>.*)/create_workflowimage$', views.create_workflowimage, name="create_workflowimage"),
    re_path(r'^recipes/(?P<pk>.*)/create_workflowinstance_from_recipe$', views.create_workflowinstance_from_recipe, name="create_workflowinstance_from_recipe"), 
    re_path(r'^recipes/(?P<pk>.*)/create_system_worflowinstances_from_recipe$', views.create_system_worflowinstances_from_recipe, name="create_system_worflowinstances_from_recipe"),

    re_path(r'^images/all$', views.workflowimages_all, name="workflowimages_all"),
    re_path(r'^images/(?P<pk>.*)/create_workflowinstance$', views.create_workflowinstance, name="create_workflowinstance"),
    re_path(r'^images/(?P<pk>.*)/delete$', views.delete_workflowimage, name="delete_workflowimage"),
    re_path(r'^images/(?P<pk>.*)/create_workflowrecipe$', views.create_workflowrecipe_from_image, name="create_workflowrecipe_from_image"),
    re_path(r'^images/(?P<pk>.*)/create_system_worflowinstances$', views.create_system_worflowinstances, name="create_system_worflowinstances"),

    re_path(r'^instances/all$', views.workflowinstances_all, name="workflowinstances_all"),

    # re_path(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

]

