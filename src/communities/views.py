from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Community, CommunityMember, Report
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
def create_report(request, community_id):
    return render(request, 'report/create_report.html', {'community_id': community_id})


# def for saving a report after creation
def save_report(request, community_id):

    # get the report data from the form
    # data should be Title, Content, Author, Resolution Method, and Media
    title = request.POST.get('title')
    content = request.POST.get('content')

    # if author is anonymous, set to None
    # else, retrieve the author from the request
    if request.user.is_authenticated:
        author = get_user_model().objects.get(email=request.user.email)
    else:
        author = None

    resolution_method = request.POST.get('resolution_method')

    # make a new Report model
    report = Report(title=title, content=content, author=author, resolution_method=resolution_method)

    # attach the report to the community
    community = get_object_or_404(Community, pk=community_id)
    report.save()
    community.reports.add(report)


    # TODO add media files

    # go back to the community dashboard (url pattern: community/<int:community_id>/dashboard/)
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community_id,]))

def view_report(request, community_id, report_id):
    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    return render(request, 'report/view_report.html', {'report': report, 'community_id': community_id})