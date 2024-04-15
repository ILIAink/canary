from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from accounts.models import User
from canary.models import Notification
from communities.models import Community, CommunityMember, Report


# Create your views here.


# home view - info about the app and a link to the login page
def home(request):
   return render(request, 'home.html')


# login view - redirect to user dashboard by default, next otherwise
def login(request):
   return render(request, 'login.html')


# dashboard view - displays the user's dashboard
def dashboard(request):
   if request.user.is_authenticated:
       notifications = Notification.objects.filter(recipient=request.user, is_viewed=False)
       if len(notifications) <= 0:
           num_notifications = ""
       elif 0 < len(notifications) < 9:
           num_notifications = len(notifications)
       else:
           num_notifications = "9+"
            
       user_communities = CommunityMember.objects.filter(member=request.user, is_admin=False)
       admin_communities = CommunityMember.objects.filter(member=request.user, is_admin=True)
       is_super_user = request.user.is_superuser
       both_empty = False
       if(not(user_communities) and not(admin_communities)):
            both_empty = True


       return render(request, 'dashboard/dashboard_user_final.html', {'user': request.user, 'user_communities': user_communities, "admin_communities": admin_communities, 'both_empty': both_empty, 'num_notifications': num_notifications})

   else:
       # Handle the case when the user is not authenticated, perhaps redirect to login page
       return render(request, 'account/login.html')


# notifications
def notifications(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("canary:"))
    
    notifs = Notification.objects.filter(recipient=request.user)
    notif_dict = {}

    for notif in notifs:
        notif_dict[notif]=notif.is_viewed
        if notif.is_viewed == False:
            notif.is_viewed=True
            notif.save()
    
    notif_dict = dict(reversed(list(notif_dict.items())))
    
    return render(request, 'notifications.html', {'notifications': notif_dict})

def delete_notification(request):
    notif_id = request.POST.get('notif_id')
    notification = get_object_or_404(Notification, pk=notif_id)
    notification.delete()
    
    return HttpResponseRedirect(reverse("canary:notifications"))


def clear_all_notifications(request):
    Notification.objects.filter(recipient=request.user).all().delete()
    
    return HttpResponseRedirect(reverse("canary:notifications"))

def create_notif(recipient_id, report_id, community_id, content):
    recipient = get_object_or_404(User, pk=recipient_id)
    report = get_object_or_404(Report, pk=report_id)
    community = get_object_or_404(Community, pk=community_id)
    notification = Notification(recipient=recipient, report=report, community=community, content=content)

    notification.save()

# function called when new report is created to notify admins and owner
def new_report_notif(recipient_id, report_id, community_id):
    community = get_object_or_404(Community, pk=community_id)
    report = get_object_or_404(Report, pk=report_id)
    content = "New Report in {}: \"{}\"".format(community.name, report.title)
    create_notif(recipient_id=recipient_id, report_id = report_id, community_id=community_id, content=content)

# function called when report status is updated to notify reporter
def report_status_notif(recipient_id, report_id, community_id):
    community = get_object_or_404(Community, pk=community_id)
    report = get_object_or_404(Report, pk=report_id)
    content = "Report \"{}\" in {} has been marked as {}".format(report.title, community.name, report.get_status_display())
    create_notif(recipient_id=recipient_id, report_id = report_id, community_id=community_id, content=content)

# function called when an admin adds notes to a report to notify reporter
def report_notes_notif(recipient_id, report_id, community_id):
    community = get_object_or_404(Community, pk=community_id)
    report = get_object_or_404(Report, pk=report_id)
    content = "An admin has responded to your report \"{}\" in {}".format(report.title, community.name)
    create_notif(recipient_id=recipient_id, report_id = report_id, community_id=community_id, content=content)




