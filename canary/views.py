from django.shortcuts import render

# Create your views here.

# home view - info about the app and a link to the login page
def home(request):
    return render(request, 'home.html')

# login view - a simple login page
def login(request):
    return render(request, 'login.html')

# dashboard view - a simple dashboard page
# TODO implement this
def dashboard(request):
    return render(request, 'dashboard.html')
