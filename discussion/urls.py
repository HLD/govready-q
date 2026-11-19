from django.urls import include, re_path

from django.contrib import admin
admin.autodiscover()

import discussion.views as views

urlpatterns = [
    re_path(r'^_discussion_comment_draft', views.update_discussion_comment_draft, name="discussion-comment-draft"),
    re_path(r'^_discussion_comment_submit', views.submit_discussion_comment, name="discussion-comment-submit"),
    re_path(r'^_discussion_comment_edit', views.edit_discussion_comment, name="discussion-comment-edit"),
    re_path(r'^_discussion_comment_delete', views.delete_discussion_comment, name="discussion-comment-delete"),
    re_path(r'^_discussion_comment_react', views.save_reaction, name="discussion-comment-react"),
    re_path(r'^_discussion_comment_attachments', views.create_attachments, name="discussion-comment-create-attachments"),
    re_path(r'^_discussion_poll', views.poll_for_events, name="discussion_poll_for_events"),
    re_path(r'^attachment/(\d+)', views.download_attachment, name="discussion-attachment"),
]

