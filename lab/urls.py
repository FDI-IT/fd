from django.conf.urls import url
from lab import views

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^inventory', views.inventory),
    url(r'^finished_product_labels/', views.finished_product_labels),
    url(r'^rm_labels/', views.rm_labels),
    url(r'^experimental_labels/$', views.experimental_labels),
    url(r'^ingredient_label/$', views.ingredient_label),
    url(r'^rm_sample_label/$', views.rm_sample_labels),
    url(r'^experimentals_by_customer/$', views.experimentals_by_customer),
    url(r'^experimentals_by_customer/(?P<customer>[\w ]+)/$', views.experimentals_by_customer_specific),
    
)
