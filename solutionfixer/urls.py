from django.conf.urls.defaults import *

urlpatterns = patterns('solutionfixer.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#    (r'^(?P<flavor_number>\d+)/$', 'flavor_review'),
#    (r'^(?P<flavor_number>\d+)/batch_sheet/$', 'batch_sheet'),
#    (r'^print_flavor/$', 'print_flavor'),
#    (r'^(?P<flavor_number>\d+)/price_update/$', 'price_update'),\
    (r'^$', 'solution_review'),
    (r'flagged$', 'flagged_review'),
    (r'^process_baserm_bypk_update$', 'process_baserm_bypk_update'),
    (r'^process_baserm_update$', 'process_baserm_update'),
    (r'^process_status_update$', 'process_status_update'),
    (r'^process_solvent_update$', 'process_solvent_update'),
    (r'^process_percentage_update$', 'process_percentage_update'),
    (r'^solution_summary$', 'solution_summary'),
    (r'^flagged_summary$', 'flagged_summary'),
    (r'^solution_summary/(?P<status>\w+)$', 'solution_summary'),
    (r'^ingredient_autocomplete$', 'ingredient_autocomplete'),
    (r'^solution_loader$', 'solution_loader'),
    (r'^post_match_guesses$', 'post_match_guesses'),
    (r'^pin_review/(?P<ingredient_id>\d+)/$', 'solution_pin_review'),
)
