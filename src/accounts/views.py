from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from accounts.models import User
from django.contrib import messages



# Create your views here.

def edit_profile(request):
    return render(request, 'account/edit_profile.html')
# save user info edits
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





