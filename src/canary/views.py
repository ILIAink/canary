from django.shortcuts import render
from communities.models import Community, CommunityMember


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
       user_communities = CommunityMember.objects.filter(member=request.user)
       if request.user.is_staff:  # Check if the user is an administrator
           return render(request, 'dashboard/dashboard_admin.html', {'user': request.user, 'user_communities': user_communities})
       else:
           return render(request, 'dashboard/dashboard_user.html', {'user': request.user, 'user_communities': user_communities})
   else:
       # Handle the case when the user is not authenticated, perhaps redirect to login page
       return render(request, 'account/login.html')