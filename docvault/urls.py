import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic.date_based import archive_index
from django.db.models import Q, F

from docvault.models import Doc
doc_list_info = {
        'queryset':Doc.objects.all(),
        'pageinate_by':100,
        'extra_context': dict({
            'page_title': 'Scanned Docs',
        },)
    }

urlpatterns = patterns('newqc.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', redirect_to, {'url': '/django/docvault/docs/'}),
    (r'^docs/$', list_detail.object_list, doc_list_info),
    
)
