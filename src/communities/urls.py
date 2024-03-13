from django.urls import path

from . import views

app_name = "communities"
urlpatterns = [
    path("create_community/", views.create_community, name="create_community"),
    path("save_community", views.save_community, name="save_community"),
    path("admin_community_home/", views.admin_community_home, name="admin_community_home"),

    # urls for submitting and viewing a report submitted to a given community
    # note that all report views and templates are in the reports app
    path("<int:community_id>/create_report/", views.create_report, name="create_report"),
    path("<int:community_id>/save_report/", views.save_report, name="save_report"),
    path("<int:community_id>/dashboard/", views.community_dashboard, name="dashboard"),
    path("<int:community_id>/report/<int:report_id>/", views.view_report, name="view_report"),
]