from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from accounts.models import User
from django.contrib import messages



# Create your views here.

@login_required
def edit_profile(request):
    user = User.objects.get(id=request.user.id)
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    return render(request, 'account/edit_profile.html', {'username': username, 'first_name': first_name, 'last_name': last_name})

# save user info edits
@login_required
def save_profile(request):
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        user.username = username
        user.first_name = first_name
        user.last_name = last_name

        user.save()
        messages.success(request, "User Info Successfully Updated!")
        return HttpResponseRedirect(reverse("canary:dashboard"))
@login_required
def reset_password(request):
    return render(request, 'account/reset_password.html')

@login_required
def admin_dash(request):
    return render(request, 'dashboard/dash_admin_new.html')





