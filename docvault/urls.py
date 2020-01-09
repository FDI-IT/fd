import datetime

from django.conf.urls import url, include
from django.views.generic.list import ListView
from django.views.generic import RedirectView, TemplateView

from docvault.models import Doc
doc_list_info = {
        'queryset':Doc.objects.all(),
        'pageinate_by':100,
        'extra_context': dict({
            'page_title': 'Scanned Docs',
        },)
    }

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', RedirectView.as_view(url='/docvault/docs/')),
    url(r'^docs/$', ListView.as_view(**doc_list_info)),
    
)
