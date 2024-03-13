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

def join_a_community(request):
    return render(request, 'community/join_a_community.html')

def join_community_error(request):
    return render(request, 'community/join_community_error.html')

def join_success(request):
    return render(request, 'community/join_success.html')

# def for saving a community after creation
def save_community(request):

    name = request.POST.get('name')
    password = request.POST.get('password')
    description = request.POST.get('description')
    community = Community(name=name, password=password, description=description)



    # Save the community to the database
    community.save()

    admin_member = CommunityMember(community=community, is_admin=1, member=request.user)

    admin_member.save()

    return HttpResponseRedirect("admin_community_home")

def join_community(request):
    if request.method == 'POST':
        community_name = request.POST.get('name', None)
        password = request.POST.get('password', None)

        if community_name is not None and password is not None:
            try:
                # Search for the community by name
                community = Community.objects.get(name=community_name)

                # Check if the provided password matches the community password
                if community.password == password:
                    # Password matches, perform further actions here
                    # For example, you might redirect to a page displaying community details
                    member = CommunityMember(community=community, is_admin=0, member=request.user)
                    member.save()
                    return HttpResponseRedirect("join_success")
                else:
                    # Password does not match
                    return HttpResponseRedirect("join_community_error")
            except Community.DoesNotExist:
                # Community with given name does not exist
                return HttpResponseRedirect("join_community_error")
        else:
            # Invalid POST data
            return HttpResponseRedirect("join_community_error")
    else:
        # GET request, render a form to search for the community
        return HttpResponseRedirect("join_community_error")
