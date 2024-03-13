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
# TODO do we want to re-implement this, or use a single dashboard view for all users?
def admin_community_home(request):
    return render(request, 'dashboard/dashboard_community_admin.html')

def community_dashboard(request, community_id):
    # get the community object
    community = get_object_or_404(Community, pk=community_id)

    # get the community members
    members = CommunityMember.objects.filter(community=community)

    # get the reports submitted to the community
    reports = community.reports.all()

    return render(request, 'community/community_dashboard.html', {'community': community, 'members': members, 'reports': reports})


# def for saving a community after creation
def save_community(request):

    name = request.POST.get('name')
    password = request.POST.get('password')
    description = request.POST.get('description')
    community = Community(name=name, password=password, description=description)



    # Save the report to the database
    community.save()

    # find the user who created the community by email address
    user = get_user_model().objects.get(email=request.user.email)

    # create a community member object for the user who created the community
    admin_member = CommunityMember(community=community, member=user, is_admin=True)

    admin_member.save()

    # url pattern: community/<int:community_id>/dashboard/
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community.id,]))


# views for report management for this community
# use the report app for the actual report views and templates
# TODO debugging this is the next step
def create_report(request, community_id):
    # call the report create view from the reports app
    return HttpResponseRedirect(reverse("reports:create_report", args=[community_id,]))
def save_report(request, community_id):
    # call the report save view from the reports app
    return HttpResponseRedirect(reverse("reports:save_report", args=[community_id,]))

def view_report(request, report_id):
    # call the report view from the reports app
    return HttpResponseRedirect(reverse("reports:view_report", args=[report_id,]))