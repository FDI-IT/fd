from django.conf.urls import url, include
from salesorders import views

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^(?P<sales_order_number>\d+)/$', views.sales_order_review, name='sales_review'),
    url(r'^$', views.sales_order_report),
    url(r'^customer/(?P<customer_pk>\d+)/$', views.customer_report),
    url(r'^customer/(?P<customer_pk>\d+)/customer_spec_sheet/(?P<flavor_number>\d+)/$', views.customer_spec_sheet),
    url(r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/$', views.customer_spec_list),
    #url(r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/edit/(?P<spec_id>\d+)/$', views.edit_customer_spec),
    url(r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/add/$', views.edit_customer_spec),
    url(r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/delete/(?P<spec_id>\d+)/$', views.delete_customer_spec),
    #url(r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/$', views.edit_customer_specs),
    url(r'^product/$', views.sales_order_by_product),
    url(r'^lineitem/$', views.sales_order_by_lineitem),
    url(r'^upload_report/$', views.upload_report),
    url(r'^coloractivation$', views.coloractivation),
    url(r'^flavors_ordered/$', views.flavors_ordered),
    url(r'^ingredients_required/$', views.ingredients_required),
)