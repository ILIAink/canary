from django.urls import path

from . import views

app_name = "reports"
urlpatterns = [
    path("create_report/", views.create_report, name="create_report"),
    path("save_report", views.save_report, name="save_report"),
]