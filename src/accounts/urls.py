from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("save_profile/", views.save_profile, name="save_profile"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("admin_dash/", views.admin_dash, name="admin_dash")
]
