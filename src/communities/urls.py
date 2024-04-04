from django.urls import path, re_path
from . import views

app_name = "communities"
urlpatterns = [
    path("create_community/", views.create_community, name="create_community"),
    path("save_community", views.save_community, name="save_community"),
    path("admin_community_home/", views.admin_community_home, name="admin_community_home"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/dashboard/$", views.community_dashboard, name="dashboard"),

    # community joining / leaving
    path("join_community_error/<str:error_type>/", views.join_community_error, name="join_community_error"),
    path("join_success/", views.join_success, name="join_success"),

    # special url for invite links
    re_path(r"^generate_invite/(?P<community_id>[0-9a-f-]+)/$", views.generate_invite_link, name="generate_invite"),
    re_path(r"^invite/(?P<token>[0-9a-f-]+)/$", views.join_community_by_invite, name="join_community_by_invite"),

    # url for submitting anonymously through a link
    re_path(r"^(?P<token>[0-9a-f-]+)/anon_report/", views.create_anonymous_report, name="create_anonymous_report"),

    # urls for report management
    re_path(r"^(?P<community_id>[0-9a-f-]+)/create_report/", views.create_report, name="create_report"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/save_report/", views.save_report, name="save_report"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/report/(?P<report_id>[0-9a-f-]+)/$", views.view_report, name="view_report"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/report/(?P<report_id>[0-9a-f-]+)/edit/", views.edit_report, name="edit_report"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/report/(?P<report_id>[0-9a-f-]+)/delete/", views.delete_report, name="delete_report"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/change_admin_status/(?P<member_id>[0-9a-f-]+)/", views.change_admin_status,
            name="change_admin_status"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/remove_member/(?P<member_id>[0-9a-f-]+)/", views.remove_member,
            name="remove_member"),
    re_path(r"^(?P<community_id>[0-9a-f-]+)/community_members/", views.community_members, name="community_members"),
]