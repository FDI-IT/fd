from django.conf.urls import url, include
from solutionfixer import views

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#    url(r'^(?P<flavor_number>\d+)/$', views.flavor_review),
#    url(r'^(?P<flavor_number>\d+)/batch_sheet/$', views.batch_sheet),
#    url(r'^print_flavor/$', views.print_flavor),
#    url(r'^(?P<flavor_number>\d+)/price_update/$', views.price_update),\
    url(r'^$', views.solution_review),
    url(r'flagged$', views.flagged_review),
    url(r'^process_baserm_bypk_update$', views.process_baserm_bypk_update),
    url(r'^process_baserm_update$', views.process_baserm_update),
    url(r'^process_status_update$', views.process_status_update),
    url(r'^process_solvent_update$', views.process_solvent_update),
    url(r'^process_percentage_update$', views.process_percentage_update),
    url(r'^solution_summary$', views.solution_summary),
    url(r'^flagged_summary$', views.flagged_summary),
    url(r'^solution_summary/(?P<status>\w+)$', views.solution_summary),
    url(r'^ingredient_autocomplete$', views.ingredient_autocomplete),
    url(r'^solution_loader$', views.solution_loader),
    url(r'^post_match_guesses$', views.post_match_guesses),
    url(r'^pin_review/(?P<ingredient_id>\d+)/$', views.solution_pin_review),
)
