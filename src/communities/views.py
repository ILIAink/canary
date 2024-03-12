from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Community, CommunityMember
from django.urls import reverse

# Create your views here.

def create_community(request):
    # TODO connect to the community creation form
    return render(request, 'community/create_community.html')


# Admin home view - displays the home view for the admin of a community
def admin_community_home(request):
    return render(request, 'dashboard/dashboard_community_admin.html')


# def for saving a community after creation
def save_community(request):

    name = request.POST.get('name')
    password = request.POST.get('password')
    description = request.POST.get('description')
    community = Community(name=name, password=password, description=description)



    # Save the report to the database
    community.save()

    admin_member = CommunityMember(community=community, is_admin=1, member=request.user)

    admin_member.save()

    return HttpResponseRedirect("admin_community_home")

