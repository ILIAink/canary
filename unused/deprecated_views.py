from django.http import HttpResponseRedirect

from django.apps import apps
Community = apps.get_model('communities', 'Community')
Community_Member = apps.get_model('communities', 'CommunityMember')



def join_community(request):
    if request.method == 'POST':
        community_name = request.POST.get('name', None)
        password = request.POST.get('password', None)

        if community_name is not None and password is not None:
            try:
                # Search for the community by name
                community = Community.objects.get(name=community_name)

                # Check if the provided password matches the community password
                if community.password == password:
                    # Password matches, perform further actions here
                    # For example, you might redirect to a page displaying community details
                    member = CommunityMember(community=community, is_admin=0, member=request.user)
                    member.save()
                    return HttpResponseRedirect("join_success")
                else:
                    # Password does not match
                    return HttpResponseRedirect("join_community_error")
            except Community.DoesNotExist:
                # Community with given name does not exist
                return HttpResponseRedirect("join_community_error")
        else:
            # Invalid POST data
            return HttpResponseRedirect("join_community_error")
    else:
        # GET request, render a form to search for the community
        return HttpResponseRedirect("join_community_error")