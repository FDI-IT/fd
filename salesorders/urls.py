from django.conf.urls.defaults import *

urlpatterns = patterns('salesorders.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^(?P<sales_order_number>\d+)/$', 'sales_order_review', name='sales_review'),
    (r'^$', 'sales_order_report'),
    (r'^customer/(?P<customer_pk>\d+)/$', 'customer_report'),
    (r'^customer/(?P<customer_pk>\d+)/customer_spec_sheet/(?P<flavor_number>\d+)/$', 'customer_spec_sheet'),
    (r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/$', 'customer_spec_list'),
    (r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/edit/(?P<spec_id>\d+)/$', 'edit_customer_spec'),
    (r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/add/$', 'edit_customer_spec'),
    (r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/delete/(?P<spec_id>\d+)/$', 'delete_customer_spec'),
    #(r'^customer/(?P<customer_pk>\d+)/customer_specs/(?P<flavor_number>\d+)/$', 'edit_customer_specs'),
    (r'^product/$', 'sales_order_by_product'),
    (r'^lineitem/$', 'sales_order_by_lineitem'),
    (r'^upload_report/$', 'upload_report'), 
    (r'^coloractivation$', 'coloractivation'),
    (r'^flavors_ordered/$', 'flavors_ordered'),
    (r'^ingredients_required/$', 'ingredients_required'),
)