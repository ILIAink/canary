from django.shortcuts import render

from django.http import HttpResponseRedirect
from .models import Report
from django.urls import reverse

# Create your views here.

def create_report(request):
    return render(request, 'create_report.html')


# def for saving a report after creation
def save_report(request, community):

    name = request.POST.get('name')
    password = request.POST.get('password')
    description = request.POST.get('description')
    admin = request.user

    report = Report(name=name, password=password, description=description)

    # Save the report to the database
    report.save()

    # TODO add author info

    return HttpResponseRedirect(reverse("admin_community_home", args=community.name))