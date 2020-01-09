from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from homepage import views as homepage_views
from personnel import views as personnel_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Example:
    # url(r'^fd/', include('foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #
    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
    url(r'^vanilla/$',homepage_views.vanilla),
    url(r'^', include('homepage.urls')),
    url(r'^mysearch/', include('mysearch.urls')),
    url(r'^qc/', include('newqc.urls')),
    url(r'^haccp/', include('haccp.urls')),
    url(r'^access/', include('access.urls')),
    url(r'^lab/', include('lab.urls')),
    url(r'^batchsheet/', include('batchsheet.urls')),
    url(r'^solutionfixer/', include('solutionfixer.urls')),

    url(r'^flavor_usage/', include('flavor_usage.urls')),
    url(r'^salesorders/', include('salesorders.urls')),
    url(r'^performance_appraisal/', include('performance_appraisal.urls')),
    url(r'^invoices/', include('invoices.urls')),
    # url(r'^accounts/login/$', personnel_views.force_pwd_change,
    #  {'template_name': 'homepage/login.html'}),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='homepage/login.html')),
     # {'template_name': 'homepage/login.html'}),
    url(r'^accounts/password_change/$', personnel_views.password_change,),
    url(r'^accounts/password_change_done/$', auth_views.PasswordChangeDoneView,
     {'template_name': 'homepage/password_changed.html'}),
    url(r'^accounts/logout/$', auth_views.LogoutView,
     {'template_name': 'homepage/login.html',
      'next_page':'/accounts/login/'}),
    url(r'^history_audit/', include('history_audit.urls')),
    url(r'^export/', include('export.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^hazards/', include('hazards.urls')),
    url(r'^unified_adapter/', include('unified_adapter.urls')),
    url(r'^api/', include('api.urls')),
]

urlpatterns += staticfiles_urlpatterns()
