from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib import databrowse
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^fd/', include('foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^batchsheet/', include('batchsheet.urls')),
    (r'^vanilla/$', 'homepage.views.vanilla'),
    (r'^$', include('homepage.urls')),
    #(r'^search/$', include('haystack.urls')),
    (r'^mysearch/', include('mysearch.urls')),
    #(r'^comments/', include('django.contrib.comments.urls')),
    #(r'^base/$', 'homepage.views.base'),
    #(r'^qctwo/', include('qctwo.urls')),
    (r'^qc/', include ('newqc.urls')),
    (r'^haccp/', include ('haccp.urls')),
    (r'^access/', include ('access.urls')),
    (r'^lab/', include ('lab.urls')),
    (r'^solutionfixer/', include ('solutionfixer.urls')),

    (r'^flavor_usage/', include ('flavor_usage.urls')),
    (r'^salesorders/', include ('salesorders.urls')),
    (r'^performance_appraisal/', include ('performance_appraisal.urls')),
    (r'^invoices/', include ('invoices.urls')),
    (r'^accounts/login/$',
     'personnel.views.force_pwd_change',
     {'template_name': 'homepage/login.html'}
     ),
    (r'^accounts/password_change/$',
     'personnel.views.password_change',),
    (r'^accounts/password_change_done/$',
     'django.contrib.auth.views.password_change_done',
     {'template_name': 'homepage/password_changed.html'}),
    (r'^accounts/logout/$',
     'django.contrib.auth.views.logout',
     {'template_name': 'homepage/login.html',
      'next_page':'/django/accounts/login/'}),
    (r'^databrowse/(.*)', databrowse.site.root),
    #(r'^fdileague/', include ('fdileague.urls')),
    #(r'^players/', include ('fdileague.player_urls')),
    (r'^unified_adapter/', include ('unified_adapter.urls')),
)

from access.models import Flavor, Ingredient, ExperimentalLog, Formula

databrowse.site.register(Flavor)
databrowse.site.register(Ingredient)
databrowse.site.register(ExperimentalLog)
databrowse.site.register(Formula)
