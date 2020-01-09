from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.template import RequestContext

import reversion

from access.views import flavor_info_wrapper

from flavor_usage import models
from flavor_usage import forms

@login_required
@reversion.create_revision()
@flavor_info_wrapper
def new_usage(request, flavor):
    if request.method == 'POST':
        form = forms.UsageForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(form.instance.flavor.get_absolute_url())
    else:
        appl = models.Application(flavor=flavor)
        form = forms.UsageForm(instance=appl)
    return render(
        request,
        'flavor_usage/new_usage.html',
        {'form':form},
    )

def test(request):
    import os
    x = os.environ.keys()
    import getpass
    u = getpass.getuser()
    print x
