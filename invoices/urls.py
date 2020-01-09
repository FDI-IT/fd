from django.conf.urls import url, include
from invoices import views

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^$', views.date_summary),
    url(r'^upload_report/$', views.upload_report),
    url(r'^upload_report_lw/$', views.upload_report_lw),
    url(r'^date_summary/$', views.date_summary),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.date_detail),
)