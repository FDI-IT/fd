from production.models import Lot
from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.views.generic import list_detail
from django.template import RequestContext

@login_required
def index(request, status_message=None):
    try:
        paginator = Paginator(Lot.objects.filter(name__icontains=request.GET['name']), 80)
    except MultiValueDictKeyError:
        paginator = Paginator(Lot.objects.all(), 80)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        lots = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lots = paginator.page(paginator.num_pages)
        
    return render_to_response('flavorbase/index.html', 
                              {'list_items': lots,
                               'status_message': status_message,
                               'pagetitle': "QC Retain History by flavor number",},
                              context_instance=RequestContext(request))
@login_required
def lots_by_status(request, status):

    cursor = connection.cursor()
    cursor.execute("""
                   SELECT DISTINCT status
                   FROM production_lot""")

    return list_detail.object_list(
        request,
        queryset = Lot.objects.filter(status__iexact=status),
        paginate_by = 50,
        template_name = "qc/retains_by_status.html",
        template_object_name = "retain",
        extra_context = {"status": status,
                         "statuslinks": cursor.fetchall(),}
    )
