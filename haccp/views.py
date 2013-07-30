from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from django.http import HttpResponseRedirect
from reversion import revision
from django.contrib.auth.decorators import login_required

def index(request):
    return render_to_response('haccp/index.html')

#def water_test(request, status_message=None):
    