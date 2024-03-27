from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Community, CommunityMember, Report, UploadedFile
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

# community membership control
def join_a_community(request):
  return render(request, 'community/join_a_community.html')

def join_community_error(request):
    return render(request, 'community/join_community_error.html')

def join_success(request):
    return render(request, 'community/join_success.html')

def community_members(request, community_id):
    # Get the community object or return 404 if not found
    community = get_object_or_404(Community, id=community_id)
    # Retrieve community members for the specified community
    community_member = CommunityMember.objects.filter(community=community)

    # get the permission level of the current user
    user = get_user_model().objects.get(email=request.user.email)
    try:
        user_member = CommunityMember.objects.get(community=community, member=user)
    except CommunityMember.DoesNotExist:
        return HttpResponseRedirect(reverse("canary:dashboard"))

    user_role = 'owner' if user_member.is_owner else 'admin' if user_member.is_admin else 'member'

    # can the user remove members?
    can_remove = user_member.is_owner or user_member.is_admin

    print(user_role, can_remove)

    # Pass the community_members data to the template
    return render(request, 'community/community_members.html', {'community_id': community_id, 'community_member': community_member, 'user_role': user_role, 'can_remove': can_remove})


# def for saving a community after creation
def save_community(request):

    name = request.POST.get('name')
    password = request.POST.get('password')
    description = request.POST.get('description')
    community = Community(name=name, password=password, description=description)


    # Save the community to the database
    community.save()

    # find the user who created the community by email address
    user = get_user_model().objects.get(email=request.user.email)

    # create a community member object for the user who created the community
    admin_member = CommunityMember(community=community, member=user, is_admin=True, is_owner=True)

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

    # handle media file upload
    for file in request.FILES.getlist('media'):
        report_file = UploadedFile(report=report, file=file)
        report_file.save()

    # go back to the community dashboard (url pattern: community/<int:community_id>/dashboard/)
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community_id,]))

def view_report(request, community_id, report_id):
    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    # get the media files associated with the report
    media = report.uploadedfile_set.all()

    community = Community.objects.get(pk=community_id)

    is_admin = False
    if request.user.is_authenticated:
        user = get_user_model().objects.get(email=request.user.email)
        is_admin = user.communitymember_set.filter(community=community, is_admin=True).exists()

        print(user)
        print(is_admin)
    
    return render(request, 'report/view_report.html', {'report': report, 'media': media, 'community': community, 'is_admin': is_admin})

def edit_report(request, community_id, report_id):
    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    status = request.POST.get('status')
    notes = request.POST.get('notes')

    if status:
        report.status = status
    if notes:
        report.notes = notes

    report.save()

    # send the user back to the report view
    return HttpResponseRedirect(reverse("communities:view_report", args=[community_id, report_id]))
    
    
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


def change_admin_status(request, community_id, member_id):
    # Find the CommunityMember object to be modified
    community = get_object_or_404(Community, id=community_id)
    user = get_user_model().objects.get(id=member_id)
    # Retrieve community members for the specified community
    community_member = get_object_or_404(CommunityMember, community=community, member=user)

    # Toggle the is_admin status of the CommunityMember object
    community_member.is_admin = not community_member.is_admin
    community_member.save()
    return HttpResponseRedirect(reverse("communities:community_members", args=[community_id,]))

def remove_member(request, community_id, member_id):
    # Find the CommunityMember object to be removed
    community = get_object_or_404(Community, id=community_id)
    user = get_user_model().objects.get(id=member_id)
    # Retrieve community members for the specified community
    community_member = get_object_or_404(CommunityMember, community=community, member=user)

    # Delete the CommunityMember object
    community_member.delete()
    return HttpResponseRedirect(reverse("communities:community_members", args=[community_id,]))
