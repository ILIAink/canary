from django.urls import path

from . import views

app_name = "canary"
urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # urls for notifications
    path("notifications/", views.notifications, name="notifications"),
    path("clear_all_notifications/", views.clear_all_notifications, name="clear_all_notifications"),
    path("delete_notification/", views.delete_notification, name="delete_notification"),
]