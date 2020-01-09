from django.conf.urls import url, include
from hazards import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = (
    # Examples:
    # url(r'^$', views.ghs.views.home, name='home'),
    # url(r'^ghs/', include('ghs.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^formula_entry/$', views.formula_entry),
    url(r'^hazard_calculator/$', views.hazard_calculator),
    url(r'^hazard_calculator/ghs_product/(?P<product_id>\d+)/$', views.hazard_calculator),
    url(r'^hazard_calculator/ghs_ingredient/(?P<ingredient_id>\d+)$', views.hazard_calculator),
    url(r'^product_list/$', views.product_list),
    url(r'^safety_data_sheet/ghs_product/(?P<product_id>\d+)/$', views.safety_data_sheet),
    url(r'^ingredient_autocomplete/$', views.ingredient_autocomplete),

)
