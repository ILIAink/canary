from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect
from .models import Report
from django.urls import reverse

# Create your views here.

def create_report(request, community_id):
    return render(request, 'create_report.html', {'community_id': community_id})


# def for saving a report after creation
def save_report(request, community_id):

    name = request.POST.get('name')
    password = request.POST.get('password')
    description = request.POST.get('description')
    admin = request.user

    report = Report(name=name, password=password, description=description)

    # Save the report to the database
    report.save()

    # TODO add author info

    # go back to the community dashboard (url pattern: community/<int:community_id>/dashboard/)
    return HttpResponseRedirect(reverse("communities:dashboard", args=[community_id,]))