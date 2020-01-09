import settings

from django.conf.urls import url, include
from newqc import views as newqc_views

from django.views.generic import RedirectView, TemplateView
from django.db.models import Q, F


from access.views import SubListView
from newqc.views import NextUnresolvedLotView, ConfigView, RetainViewSet, LotViewSet, TestCardViewSet, STATUS_BUTTONS, retain_list_info, rm_retain_list_info, lot_list_info, retain_month_list, lot_list_attn, batchsheet_list_info, receiving_log_list_info

from rest_framework import routers
from rest_framework.authtoken import views
router = routers.DefaultRouter()#trailing_slash=False)

router.register(r'nextLot', NextUnresolvedLotView, 'nextLot')
router.register(r'constants', ConfigView, 'constants')
router.register(r'lots', LotViewSet, 'lot-list')
router.register(r'retains', RetainViewSet, 'retain-list')
router.register(r'testcards', TestCardViewSet, 'testcard-list')


#retain_view = SubListView.as_view(retain_list_info)

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#     url(r'^$', redirect_to, {'url': '/qc/retains/'}),
    url(r'^$', RedirectView.as_view(url='/qc/retains/')),
    url(r'^review/$', newqc_views.review),
    
    # url(r'^new_coa/(?P<lss_pk>\d+)/$', newqc_views.new_coa),
    url(r'^get_next_r_number/$', newqc_views.get_next_r_number),
    #url(r'^edit_coa/(?P<lss_pk>\d+)/$', newqc_views.edit_coa),
    url(r'^coa/(?P<coa_pk>\d+)/$', newqc_views.coa),
    url(r'^add_retains/$', newqc_views.add_retains),
    url(r'^batch_print/$', newqc_views.batch_print),
    url(r'^scrape_testcards/$', newqc_views.scrape_testcards),
    url(r'^analyze_scanned_cards/$', newqc_views.analyze_scanned_cards),
    url(r'^barcode/rm/(?P<retain_pk>\d+)/$', newqc_views.get_rm_barcode),
    url(r'^barcode/(?P<retain_pk>\d+)/$', newqc_views.get_barcode),
    url(r'^batchsheets/$', SubListView.as_view(**batchsheet_list_info)),
    url(r'^batchsheets/(?P<lot_pk>\d+)/$$', newqc_views.batchsheet_detail),
    url(r'^lots/$', newqc_views.lot_list),
    url(r'^lots/paginate(?P<paginate_by>\d+)/$', newqc_views.lot_list),
    url(r'^lots_requiring_attention/$', SubListView.as_view(**lot_list_attn)),
    url(r'^lots/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', newqc_views.lots_by_day),
    url(r'^lots/(\d{4})/(\d{2})/$', newqc_views.lots_by_month),
    url(r'^lots/(?P<lot_pk>\d+)/$', newqc_views.lot_detail),
    url(r'^lots/(?P<lot_pk>\d+)/update/(?P<update>\w+)/$', newqc_views.lot_detail),
    url(r'^lots/(?P<lot_pk>\d+)/test_results/$', newqc_views.edit_test_results),
    url(r'^lots/(?P<status>\w+)/$', newqc_views.lots_by_status),
    
    #url(r'^complex_lot_list/$', newqc_views.complex_lot_list),
    #url(r'^resolve_complex_lot/(?P<lot_pk>\d+)/$', newqc_views.resolve_complex_lot),
    
    url(r'^qc_resolver/$', newqc_views.qc_resolver),
    
    url(r'^qc_resolver/api/', include(router.urls)),
    # url(r'^api_auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', views.obtain_auth_token),
    
    
    url(r'^retains/$', SubListView.as_view(**retain_list_info)),
    url(r'^retains/(\d{4})/(\d{2})/$', newqc_views.retains_by_month),
    url(r'^retains/(\d{4})/(\d{2})/(\d{2})/$', newqc_views.retains_by_day),
    url(r'^retains/(\w+)/$', newqc_views.retains_by_status),
#     url(r'^retains/today/$', ListView.as_view(), {'queryset':Retain.objects.filter(date=datetime.date.today()),
#                                                                     'extra_context': dict({
#                                                                         'page_title': 'QC Retains',
#                                                                         'print_link': 'javascript:document.forms["retain_selections"].submit()',
#                                                                         'month_list': retain_month_list,
#                                                                     }, **STATUS_BUTTONS),}),



    url(r'^add_rm_retains/$', newqc_views.add_rm_retains),
    url(r'^rm_retains/$', SubListView.as_view(**rm_retain_list_info)),
    url(r'^rm_retains/(\d{4})/(\d{2})/$', newqc_views.rm_retains_by_month),
    url(r'^rm_retains/(\d{4})/(\d{2})/(\d{2})/$', newqc_views.rm_retains_by_day),
    url(r'^rm_retains/supplier/(\w+)/$', newqc_views.rm_retains_by_supplier),
    url(r'^rm_retains/(\w+)/$', newqc_views.rm_retains_by_status),
    
    
    url(r'^ajax_retain_status_change/$', newqc_views.ajax_retain_status_change),
    

    url(r'^flavors/(?P<flavor_number>\d+)/print/$', newqc_views.flavor_history_print),
    
    url(r'^resolve_retains/$', newqc_views.resolve_retains_any),
    #url(r'^resolve_retains/(?P<retain_pk>\d+)/$', newqc_views.resolve_retains_specific),
    
    url(r'^resolve_testcards/$', newqc_views.resolve_testcards_any),
    url(r'^resolve_testcards_ajax_post/$', newqc_views.resolve_testcards_ajax_post),
    url(r'^resolve_testcards/(?P<testcard_pk>\d+)/$', newqc_views.resolve_testcards_specific),
    url(r'^testcard_list/$', newqc_views.testcard_list),
    url(r'^passed_finder/$', newqc_views.passed_finder),
#     url(r'^no_testcards_left/$', direct_to_template, {'template':'qc/no_testcards_left.html'}),
    url(r'^no_testcards_left/$', TemplateView.as_view(template_name='about.html')),
    
    url(r'^receiving_log/$', SubListView.as_view(**receiving_log_list_info)),
    url(r'^receiving_log_print/$', newqc_views.receiving_log_print),
    url(r'^add_receiving_log/$', newqc_views.add_receiving_log),
    
    url(r'^scanned_docs/$', newqc_views.scanned_docs),
    url(r'^scanned_docs/paginate(?P<paginate_by>\d+)/$', newqc_views.scanned_docs),
    
    url(r'^migrate_scanned_docs/$', newqc_views.migrate_scanned_docs),
    url(r'^last_chance_retains/$', newqc_views.last_chance_retains),
    url(r'^last_chance_rms/$', newqc_views.last_chance_rms),
)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += (
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     )


