from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from access.models import Training
from access.views import unfinished_training_log

@login_required
def index(request):
    # alert logged in user for training
    admin = ['facemask' ,'sensory', 'firedrill', 'fltdt']
    signature = ['gbpp', 'handbook', 'osha', 'hazcom']
    unfinished_training= unfinished_training_log(request.user, request.user.groups.all()[0].name)
    return render(
        request,
        'homepage/index.html',
        {
            'unfinished_training_log':unfinished_training,
            'no_link_tests':admin,
        })


def vanilla(request):
    return render(request, 'homepage/vanilla.html')
