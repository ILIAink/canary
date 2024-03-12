from django.urls import path

from . import views

app_name = "communities"
urlpatterns = [
    path("create_community/", views.create_community, name="create_community"),
    path("save_community", views.save_community, name="save_community"),
    path("admin_community_home/", views.admin_community_home, name="admin_community_home")
]