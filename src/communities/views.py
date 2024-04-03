import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Community, CommunityMember, Report, UploadedFile, InviteLink
from django.urls import reverse
from .forms import InviteForm

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

    # log in the user if not already logged in
    if not request.user.is_authenticated:
        return render(request, 'account/login.html')

    # if the user is not a member of the community, redirect to their user dashboard
    if not CommunityMember.objects.filter(community=community, member=request.user).exists():
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # get the reports submitted to the community
    reports = community.reports.all()

    # TODO is this ever used?
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            expiration = form.cleaned_data['expiration']
            # Generate invite link logic goes here
            messages.success(request, 'Invite link created successfully.')  # You can use Django messages framework
            return redirect('communities:dashboard', community_id=community_id)
    else:
        form = InviteForm()

    return render(request, 'community/community_dashboard.html', {'community': community, 'members': members, 'reports': reports})

# community membership control
def join_a_community(request):
  return render(request, 'community/join_a_community.html')

def join_community_by_invite(request, token):
    try:
        invite_link = InviteLink.objects.get(token=token)
        if invite_link.is_valid():
            # Log in the user if not already logged in
            if not request.user.is_authenticated:
                return render(request, 'account/login.html')

            # Check if the user is already a member of the community
            if CommunityMember.objects.filter(community=invite_link.community, member=request.user).exists():
                messages.success(request, 'You are already a member of this community.')
                return redirect('communities:dashboard', community_id=invite_link.community.id)

            # Add the user to the community
            CommunityMember.objects.create(community=invite_link.community, member=request.user)

            # Update the used count of the invite link
            invite_link.used_count += 1
            invite_link.save()

            return redirect('communities:join_success')  # Redirect to join success page
        else:
            # delete the expired invite link
            return redirect('communities:join_community_error', error_type='invalid_link')  # Redirect to error page for expired or invalid link
    except InviteLink.DoesNotExist:
        return redirect('communities:join_community_error', error_type='invalid_link')  # Redirect to error page if invite link does not exist
def generate_invite_link(request, community_id):

    # get properties from request
    body = json.loads(request.body)
    expiration = body['expiration']
    max_uses = body['num_invites']
    link_type = body['link_type']

    # expiration is either '1h', '1d', '1w', '1m', or 'never'
    match expiration:
        case '1h':
            expiration_time = timezone.now() + timezone.timedelta(hours=1)
        case '1d':
            expiration_time = timezone.now() + timezone.timedelta(days=1)
        case '1w':
            expiration_time = timezone.now() + timezone.timedelta(weeks=1)
        case '1m':
            expiration_time = timezone.now() + timezone.timedelta(weeks=4)
        case 'never':
            expiration_time = timezone.now() + timezone.timedelta(weeks=52)

    if max_uses == '':
        max_uses = 1

    # generate a new invite link
    invite_link = InviteLink(community_id=community_id, expiration_time=expiration_time, max_uses=max_uses, link_type=link_type)
    invite_link.save()

    # create the actual link
    if link_type == 'join':
        # url pattern: invite/<UUID:token>/
        link_str = reverse("communities:join_community_by_invite", args=[str(invite_link.token)])
    elif link_type == 'anon':
        # url pattern: community/<UUID:community_id>/anon_report/
        link_str = reverse("communities:create_anonymous_report", args=[str(invite_link.token)])
    else:
        return HttpResponse(json.dumps({'error': 'Invalid link type'}), content_type='application/json', status=400)

    # return a response with invite link token and request headers
    return HttpResponse(json.dumps({'invite_link': link_str}), content_type='application/json')


def join_community_error(request, error_type):
    return render(request, 'community/join_community_error.html', {'error_type': error_type})

def join_success(request):
    return render(request, 'community/join_success.html')

def community_members(request, community_id):
    # Get the community object or return 404 if not found
    community = get_object_or_404(Community, id=community_id)
    # Retrieve community members for the specified community
    community_member = CommunityMember.objects.filter(community=community)

    # get the permission level of the current user
    user = get_user_model().objects.get(id=request.user.id)
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
    description = request.POST.get('description')
    community = Community(name=name, description=description)


    # Save the community to the database
    community.save()

    # find the user who created the community by ID
    user = get_user_model().objects.get(id=request.user.id)

    # create a community member object for the user who created the community
    admin_member = CommunityMember(community=community, member=user, is_admin=True, is_owner=True)

    admin_member.save()

    # url pattern: community/<UUID:community_id>/dashboard/
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community.id,]))


# views for report management for this community
def create_report(request, community_id):
    return render(request, 'report/create_report.html', {'community_id': community_id})

def create_anonymous_report(request, token):

    # get the invite link object
    invite_link = get_object_or_404(InviteLink, token=token)

    # get the community from the invite link
    community = invite_link.community

    if invite_link.is_valid():

        invite_link.used_count += 1
        invite_link.save()

        # TODO if a user is logged in when they use the link, their report is not anonymous (it should be)
        return render(request, 'report/create_report.html', {'community_id': community.id})
    else:
        # delete the expired invite link
        return redirect('communities:join_community_error', error_type='invalid_link')


# def for saving a report after creation
def save_report(request, community_id):

    # get the report data from the form
    # data should be Title, Content, Author, Resolution Method, and Media
    title = request.POST.get('title')
    content = request.POST.get('content')

    # if author is anonymous, set to None
    # else, retrieve the author from the request
    if request.user.is_authenticated:
        author = get_user_model().objects.get(id=request.user.id)
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
    messages.success(request, 'Report submitted!')
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community_id,]))


def view_report(request, community_id, report_id):
    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    # get the media files associated with the report
    media = report.uploadedfile_set.all()

    community = Community.objects.get(pk=community_id)

    is_admin = False
    if request.user.is_authenticated:
        user = get_user_model().objects.get(id=request.user.id)
        is_admin = user.communitymember_set.filter(community=community, is_admin=True).exists()

        if is_admin and report.status == 'NEW':
            report.status = 'INP'
            report.save()
    
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

def delete_report(request, community_id, report_id):
    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    report.delete()

    # send the user back to the community dashboard
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community_id,]))

# TODO delete this (deprecated)
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
