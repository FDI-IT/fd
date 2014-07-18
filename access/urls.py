from django.conf.urls.defaults import *

urlpatterns = patterns('access.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^(?P<flavor_number>\d+)/$', 'ft_review', name='flavor_review'),
    (r'(?P<flavor_number>\d+)/spec_sheet/$', 'spec_sheet'),
    (r'(?P<flavor_number>\d+)/spec_list/$', 'specification_list'),
    (r'(?P<flavor_number>\d+)/spec_list/edit/(?P<spec_id>\d+)/$', 'edit_spec'),
    (r'(?P<flavor_number>\d+)/spec_list/add/$', 'edit_spec'),
    (r'(?P<flavor_number>\d+)/spec_list/delete/(?P<spec_id>\d+)/$', 'delete_spec'),
    (r'^(?P<flavor_number>\d+)/batch_sheet/$', 'batch_sheet'),
    (r'^(?P<flavor_number>\d+)/formula_info_merge/$', 'formula_info_merge'),
    (r'^(?P<flavor_number>\d+)/recalculate/$', 'recalculate_flavor_view'),
    (r'^(?P<flavor_number>\d+)/batch_sheet/$', 'batch_sheet'),
    (r'^(?P<flavor_number>\d+)/formula_entry/$', 'formula_entry'),
    (r'^(?P<flavor_number>\d+)/print_review/$', 'print_review'),
    (r'^(?P<flavor_number>\d+)/reconcile_specs/$', 'reconcile_specs'),
    #(r'^(?P<spec_pk>\d+)/edit_spec/$', 'edit_spec'),    
    (r'^experimental/(?P<experimentalnum>\d+)/print_review/$', 'experimental_print_review'),
    (r'^tsr/new/$', 'new_tsr'),
    (r'^tsr/(?P<tsr_number>\d+)/$', 'tsr_review'),
    (r'^tsr/(?P<tsr_number>\d+)/tsr_entry/$', 'tsr_entry'),
    (r'^process_tsrli_update/$', 'process_tsrli_update'),
    (r'^purchase/new/$', 'new_po'),
    (r'^purchase/(?P<po_number>\d+)/$', 'po_review'),
    (r'^purchase/(?P<po_number>\d+)/print/$', 'po_review_print'),
    (r'^purchase/(?P<po_number>\d+)/po_entry/$', 'po_entry'),
    (r'^process_cell_update/$', 'process_cell_update'),
    (r'^process_filter_update/$', 'process_filter_update'),
    (r'^ingredient_autocomplete/$', 'ingredient_autocomplete'),
    (r'^digitized_entry/$', 'digitized_entry'),
    (r'^process_digitized_paste/$', 'process_digitized_paste'),
    (r'^table_to_csv$', 'table_to_csv'),
    (r'^get_ingredient_option_list$', 'get_ingredient_option_list'),
    (r'^db_ops$', 'db_ops'),
    (r'^ingredient_replacer/$', 'ingredient_replacer'),
    (r'^ingredient_replacer_preview/(?P<old_ingredient_id>\d+)/(?P<new_ingredient_id>\d+)/$', 'ingredient_replacer_preview'),
    (r'^location_entry/$', 'location_entry'),
    (r'^$', 'flavor_search'),
    (r'^(?P<flavor_number>\d+)/barcode/$', 'get_barcode'),
    (r'^(?P<flavor_number>\d+)/gzl/$', 'gzl'),
    (r'^ingredient/pin_review/(?P<ingredient_id>\d+)/$', 'ingredient_pin_review'),
    (r'^ingredient/(?P<ingredient_rmc>\d+)/$', 'ingredient_review'),
    (r'^ingredient/pin_review/(?P<ingredient_id>\d+)/gzl/$', 'ingredient_gzl_review'),
    (r'^ingredient/activate/(?P<raw_material_code>\d+)/$', 'ingredient_activate'),
    (r'^ingredient/activate/discontinue_all/(?P<ingredient_id>\d+)/$', 'ingredient_activate'),
    (r'^experimental/(?P<experimentalnum>\d+)/formula_entry/$', 'experimental_formula_entry'),
    (r'^experimental/(?P<experimentalnum>\d+)/$', 'experimental_review'),
    (r'^experimental/(?P<experimentalnum>\d+)/recalculate/$', 'recalculate_experimental'),
    (r'^experimental/(?P<experimentalnum>\d+)/approve/$', 'approve_experimental'),
    (r'^experimental/(?P<experimentalnum>\d+)/edit/$', 'experimental_edit'),
    (r'^experimental/(?P<experimentalnum>\d+)/name_edit/$', 'experimental_name_edit'),
    (r'^experimental/(?P<experimentalnum>\d+)/add_formula/$', 'experimental_add_formula'),
    (r'^digitized/(?P<experimentalnum>\d+)/$', 'digitized_review'),
    (r'^ft/(?P<flavor_number>\d+)/$', 'ft_review'),
    (r'^ajax_dispatch/$', 'ajax_dispatch'),
    (r'^similar/$', 'jil_object_list'),
    (r'^new_ex/$', 'new_ex_wizard'),
    (r'^new_rm/$', 'new_rm_wizard_launcher'),
    (r'^new_rm/basic/$', 'new_rm_wizard'),
    (r'^new_rm/solution/$', 'new_solution_wizard'),
    (r'^new_rm/flavor/(?P<flavor_number>\d+)/$', 'new_rm_wizard_flavor'),
    (r'^new_rm/rm/(?P<ingredient_pk>\d+)/$', 'new_rm_wizard_rm'),
    (r'^allergen_list/$', 'allergen_list'),
    (r'^rm_allergen_list/$', 'rm_allergen_list'),
    (r'^angularjs_test/$', 'angularjs_test'),
    (r'^ingredient_comparison_reports/$', 'ingredient_comparison_reports'),
    (r'^upload_cas_fema/$', 'upload_cas_fema'),
    (r'^preview_cas_fema/$', 'preview_cas_fema'),
)

