from django.conf.urls import url, include
from mysearch import views

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
   # url(r'^$', views.index),
    
    url(r'^$', views.search),
    url(r'^access/alternate_rm/$', views.alternate_rm),
    url(r'^access/new_pin_flavor/$', views.new_pin_flavor),
    url(r'^print/$', views.print_search),

    url(r'^flavor_search/$', views.flavor_search),

)
