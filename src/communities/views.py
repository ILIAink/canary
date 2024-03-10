from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Community, CommunityMember
from django.urls import reverse

# Create your views here.

def create_community(request):
    return render(request, 'create_community.html')


# Admin home view - displays the home view for the admin of a community
def admin_community_home(request):
    return render(request, 'communityadmin/admin_community_home.html')


# def for saving a community after creation
def save_community(request):

    name = request.POST.get('name')
    password = request.POST.get('password')
    admin = request.user

    community = Community(name=name, password=password)

    # Save the report to the database
    community.save()

    adminmember = CommunityMember(community=community, admin=1, member=admin)

    adminmember.save()

    return HttpResponseRedirect(reverse("admin_community_home", args=community.name))

