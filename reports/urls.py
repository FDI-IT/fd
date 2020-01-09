import datetime

from django.conf.urls import url, include
from reports import views


urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
   # url(r'^$', views.reports_home),
    url(r'^lot_summary/$', views.lot_summary),
    url(r'^lots_by_person/$', views.lots_by_person),
    url(r'^experimental_log/$', views.experimental_log),
    url(r'^experimental_log_exclude/$', views.experimental_log_exclude),
    url(r'^conversions_by_person/$', views.conversions_by_person),
    url(r'^formula_usage_summary/$', views.formula_usage_summary),
    url(r'^sales_by_person/$', views.sales_by_person),
    #url(r'^(?P<flavor_number>\d+)/batch_sheet/$', views.batch_sheet),

)

