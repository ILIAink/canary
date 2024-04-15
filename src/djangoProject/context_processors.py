from canary.models import Notification

# passes the number of notifications the user has to the template
def notifications_count(request):
    if not request.user.is_authenticated:
        return {'notifications_count': 0}

    notifs = Notification.objects.filter(recipient=request.user, is_viewed=False)
    return {'notifications_count': len(notifs)}
