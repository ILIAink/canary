import json
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Community, CommunityMember, Report, UploadedFile, InviteLink
from django.urls import reverse
from canary.views import new_report_notif, report_status_notif, report_notes_notif


# helper method to ensure user is able to view the community/report they are trying to access
# silently redirects to their user dashboard if not
def check_user_access(request, page_type, level='member', community_id=None, report_id=None):
    if not request.user.is_authenticated:
        return False

    if page_type == 'community':
        community = get_object_or_404(Community, pk=community_id)
        if not CommunityMember.objects.filter(community=community, member=request.user).exists():
            return False
    elif page_type == 'report':
        community = get_object_or_404(Community, pk=community_id)
        report = get_object_or_404(Report, pk=report_id)
        if not CommunityMember.objects.filter(community=community, member=request.user, is_admin=True).exists()\
                and not report.author == request.user:
            return False

    if level == 'admin':
        community = get_object_or_404(Community, pk=community_id)
        if not CommunityMember.objects.filter(community=community, member=request.user, is_admin=True).exists():
            return False
    elif level == 'owner':
        community = get_object_or_404(Community, pk=community_id)
        if not CommunityMember.objects.filter(community=community, member=request.user, is_owner=True).exists():
            return False

    return True


def create_community(request):
    return render(request, 'community/create_community.html')


def edit_community_redirect(request, community_id):
    return render(request, 'community/edit_community.html', context={'community_id': community_id})


@login_required
def edit_community(request):

    # make sure the user is a community admin
    if not check_user_access(request, 'community', community_id=request.POST.get('community_id'), level='admin'):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    community = get_object_or_404(
        Community, pk=request.POST.get('community_id'))
    new_description = request.POST.get('community_description')
    new_name = request.POST.get('community_name')

    # validate the new info
    if re.match(r"^\s*$", new_name) or len(new_name) > 50:
        messages.error(request, 'Invalid community name. Please try again.')
        return HttpResponseRedirect(reverse("communities:edit_community_redirect", args=[community.id]))
    if re.match(r"^\s*$", new_description) or len(new_description) > 500:
        messages.error(
            request, 'Invalid community description. Please try again.')
        return HttpResponseRedirect(reverse("communities:edit_community_redirect", args=[community.id]))

    community.description = new_description
    community.name = new_name
    community.updated_at = timezone.now()
    community.save()
    return redirect('communities:dashboard', community_id=request.POST.get('community_id'))


def leave_community(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    user_id = request.POST.get('user_id')
    CommunityMember.objects.filter(
        community=community, member=request.user).delete()
    return redirect('canary:dashboard')


@login_required
def community_dashboard(request, community_id):

    # make sure the user is a community member
    if not check_user_access(request, 'community', community_id=community_id):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # get the community object
    community = get_object_or_404(Community, pk=community_id)

    # get the community members
    members = CommunityMember.objects.filter(community=community)

    is_admin = False
    # get the reports submitted to the community if admin, else only get reports submitted by the user
    if CommunityMember.objects.get(community=community, member=request.user).is_admin:
        reports = community.reports.all()
        is_admin = True
    else:
        reports = Report.objects.filter(
            community=community, author=request.user)

    return render(request, 'community/community_dashboard.html', {'community': community, 'members': members, 'reports': reports, 'is_admin': is_admin, 'community_id': community_id})


def join_community_by_invite(request, token):
    try:
        invite_link = InviteLink.objects.get(token=token)
        if invite_link.is_valid():
            # Log in the user if not already logged in
            if not request.user.is_authenticated:
                return render(request, 'account/login.html')

            # Check if the user is already a member of the community
            if CommunityMember.objects.filter(community=invite_link.community, member=request.user).exists():
                messages.success(
                    request, 'You are already a member of this community.')
                return redirect('communities:dashboard', community_id=invite_link.community.id)

            # Add the user to the community
            CommunityMember.objects.create(
                community=invite_link.community, member=request.user)

            # Update the used count of the invite link
            invite_link.used_count += 1
            invite_link.save()

            # Redirect to join success page
            return redirect('communities:join_success')
        else:
            # delete the expired invite link
            # Redirect to error page for expired or invalid link
            return redirect('communities:join_community_error', error_type='invalid_link')
    except InviteLink.DoesNotExist:
        # Redirect to error page if invite link does not exist
        return redirect('communities:join_community_error', error_type='invalid_link')


def generate_invite_link(request, community_id):

    # if the user is not logged in, redirect to the site home page
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("canary:"))

    # make sure the user is a community admin
    if not check_user_access(request, 'community', community_id=community_id, level='admin'):
        return HttpResponseRedirect(reverse("canary:dashboard"))

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
    invite_link = InviteLink(community_id=community_id,
                             expiration_time=expiration_time, max_uses=max_uses, link_type=link_type)
    invite_link.save()

    # create the actual link
    if link_type == 'join':
        # url pattern: invite/<UUID:token>/
        link_str = reverse("communities:join_community_by_invite", args=[
                           str(invite_link.token)])
    elif link_type == 'anon':
        # url pattern: community/<UUID:community_id>/anon_report/
        link_str = reverse("communities:create_anonymous_report", args=[
                           str(invite_link.token)])
    else:
        return HttpResponse(json.dumps({'error': 'Invalid link type'}), content_type='application/json', status=400)

    # return a response with invite link token and request headers
    return HttpResponse(json.dumps({'invite_link': link_str}), content_type='application/json')


def join_community_error(request, error_type):
    return render(request, 'community/join_community_error.html', {'error_type': error_type})


def join_success(request):
    return render(request, 'community/join_success.html')


@login_required
def community_members(request, community_id):

    # make sure the user has access to the community
    if not check_user_access(request, 'community', community_id=community_id):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # Get the community object or return 404 if not found
    community = get_object_or_404(Community, id=community_id)
    # Retrieve community members for the specified community
    community_member = CommunityMember.objects.filter(community=community)

    # get the permission level of the current user
    user_member = CommunityMember.objects.get(
        community=community, member=request.user)

    user_role = 'owner' if user_member.is_owner else 'admin' if user_member.is_admin else 'member'

    # can the user remove members?
    can_remove = user_member.is_owner or user_member.is_admin

    # Pass the community_members data to the template
    return render(request, 'community/community_members.html', {'community_id': community_id, 'community_member': community_member, 'user_role': user_role, 'can_remove': can_remove})


@login_required
def make_owner(request, community_id, member_id):
    # make sure the user has access to the community
    if not check_user_access(request, 'community', level='owner', community_id=community_id):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # Get the community object or return 404 if not found
    community = get_object_or_404(Community, id=community_id)
    # Retrieve community members for the specified community
    community_member = CommunityMember.objects.filter(community=community)

    # get the permission level of the current user
    user_member = CommunityMember.objects.get(community=community, member=request.user)

    user_role = 'owner' if user_member.is_owner else 'admin' if user_member.is_admin else 'member'

    # can the user remove members?
    can_remove = user_member.is_owner or user_member.is_admin

    return render(request, 'community/make_owner.html', {'community_id': community_id, 'community_member': community_member, 'user_role': user_role, 'can_remove': can_remove})



# def for saving a community after creation
@login_required
def save_community(request):

    name = request.POST.get('name')
    description = request.POST.get('description')
    community = Community(name=name, description=description)

    # if the community info is invalid, warn the user and redirect back to the create community page
    if re.match(r"^\s*$", name) or len(name) > 50:
        messages.error(request, 'Invalid community name. Please try again.')
        return HttpResponseRedirect(reverse("communities:create_community"))
    if re.match(r"^\s*$", description) or len(description) > 500:
        print(description)
        messages.error(
            request, 'Invalid community description. Please try again.')
        return HttpResponseRedirect(reverse("communities:create_community"))

    # Save the community to the database
    community.save()

    # find the user who created the community by ID
    user = get_user_model().objects.get(id=request.user.id)

    # create a community member object for the user who created the community
    admin_member = CommunityMember(
        community=community, member=user, is_admin=True, is_owner=True)

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

        if request.user.is_authenticated:
            # if the user is logged in, log them out
            messages.info(
                request, 'You are already logged in. Please log out to submit an anonymous report.')
            # TODO once we have a custom logout page, pass the context through so the user can still submit
            return render(request, 'account/logout.html')

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
    anonymous = request.POST.get('anonymous')

    # validate the report content
    if re.match(r"^\s*$", title) or len(title) > 50:
        messages.error(request, 'Invalid report title. Please try again.')
        return HttpResponseRedirect(reverse("communities:create_report", args=[community_id,]))
    if re.match(r"^\s*$", content) or len(content) > 2000:
        messages.error(request, 'Invalid report content. Please try again.')
        return HttpResponseRedirect(reverse("communities:create_report", args=[community_id,]))

    # if author is anonymous, or the anonymous checkbox is set, set to None
    # else, retrieve the author from the request

    if request.user.is_authenticated and anonymous is None:
        author = get_user_model().objects.get(id=request.user.id)
    else:
        author = None

    resolution_method = request.POST.get('resolution_method')

    # make a new Report model
    report = Report(title=title, content=content, author=author,
                    resolution_method=resolution_method)

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

    # send notif to community admins and owner
    owner = CommunityMember.objects.filter(community=community, is_owner=True)
    admins = CommunityMember.objects.filter(community=community, is_admin=True)

    owner_and_admins = owner | admins

    for recipient in owner_and_admins:
        recipient_id = recipient.member.id
        new_report_notif(recipient_id=recipient_id,
                         report_id=report.id, community_id=community_id)

    return HttpResponseRedirect(reverse("communities:dashboard", args=[community_id,]))


@login_required
def view_report(request, community_id, report_id):

    # make sure the user can view the report
    if not check_user_access(request, 'report', community_id=community_id, report_id=report_id):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    # get the media files associated with the report
    media = report.uploadedfile_set.all()

    community = Community.objects.get(pk=community_id)

    is_admin = False
    if request.user.is_authenticated:
        user = get_user_model().objects.get(id=request.user.id)
        is_admin = user.communitymember_set.filter(
            community=community, is_admin=True).exists()

        if is_admin and report.status == 'NEW':
            report.status = 'INP'
            report.save()
            if report.author is not None:
                report_status_notif(
                    recipient_id=report.author.id, report_id=report_id, community_id=community_id)

    return render(request, 'report/view_report.html', {"community_id": community_id, 'report': report, 'media': media, 'community': community, 'is_admin': is_admin})


@login_required
def edit_report(request, community_id, report_id):

    # make sure the user is a community admin
    if not check_user_access(request, 'community', community_id=community_id, level='admin'):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    status = request.POST.get('status')
    notes = request.POST.get('notes')

    old_status = report.status
    if status:
        report.status = status
    if notes and len(notes) < 2000:
        report.notes = notes

    report.save()
    messages.success(request, "Report successfully updated")

    # send notif to reporter
    if report.author is not None:
        recipient_id = report.author.id
        if status and old_status != status:
            report_status_notif(recipient_id=recipient_id,
                                report_id=report_id, community_id=community_id)
        if notes:
            report_notes_notif(recipient_id=recipient_id,
                               report_id=report_id, community_id=community_id)

    # send the user back to the report view
    return HttpResponseRedirect(reverse("communities:view_report", args=[community_id, report_id]))


@login_required
def delete_report(request, community_id, report_id):

    # make sure the user is an admin of the community
    if not check_user_access(request, 'community', community_id=community_id, level='admin'):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # get the report object
    report = get_object_or_404(Report, pk=report_id)

    report.delete()
    messages.success(request, "Report successfully deleted")

    # send the user back to the community dashboard
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community_id,]))


@login_required
def change_admin_status(request, community_id, member_id):

    # make sure the user is a community admin
    if not check_user_access(request, 'community', community_id=community_id, level='admin'):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # Find the CommunityMember object to be modified
    community = get_object_or_404(Community, id=community_id)
    user = get_user_model().objects.get(id=member_id)
    # Retrieve community members for the specified community
    community_member = get_object_or_404(
        CommunityMember, community=community, member=user)

    # Toggle the is_admin status of the CommunityMember object
    community_member.is_admin = not community_member.is_admin
    community_member.save()

    if not check_user_access(request, 'community', community_id=community_id, level='admin'):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    return HttpResponseRedirect(reverse("communities:community_members", args=[community_id,]))


@login_required
def remove_member(request, community_id, member_id):

    # make sure the user is a community admin
    if not check_user_access(request, 'community', community_id=community_id, level='admin'):
        return HttpResponseRedirect(reverse("canary:dashboard"))

    # Find the CommunityMember object to be removed
    community = get_object_or_404(Community, id=community_id)
    user = get_user_model().objects.get(id=member_id)
    # Retrieve community members for the specified community
    community_member = get_object_or_404(
        CommunityMember, community=community, member=user)

    # Delete the CommunityMember object
    community_member.delete()
    return HttpResponseRedirect(reverse("communities:community_members", args=[community_id,]))

@login_required
def save_owner(request, community_id, member_id):
    community_cur_owner = get_object_or_404(CommunityMember, community=community_id, is_owner=True)
    community_new_owner = get_object_or_404(CommunityMember, community=community_id, member=member_id)
    community_cur_owner.is_owner = False
    community_cur_owner.is_admin = True
    community_new_owner.is_owner = True
    community_new_owner.is_admin = True
    community_cur_owner.save()
    community_new_owner.save()
    return HttpResponseRedirect(reverse("communities:community_members", args=[community_id,]))
