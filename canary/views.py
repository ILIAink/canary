from django.shortcuts import render

# Create your views here.

# home view - info about the app and a link to the login page
def home(request):
    return render(request, 'home.html')

# login view - a simple login page
def login(request):
    return render(request, 'login.html')

# dashboard view - displays the user's dashboard
def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  # Check if the user is an administrator
            return render(request, 'dashboard/dashboard_admin.html')
        else:
            return render(request, 'dashboard/dashboard_user.html')
    else:
        # Handle the case when the user is not authenticated, perhaps redirect to login page
        return render(request, 'account/login.html')