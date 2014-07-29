jQuery.ajaxSettings.traditional = true;

var last_index=50;
var hasNextPage = true;

var initial_sources = {};

$.fn.getSuggestedResults = function(my_solution_array, my_row_array) {
	jQuery.post('/solutionfixer/post_match_guesses',
		{
			solution_ids: my_solution_array,
			row_ids: my_row_array
		},
		function (data) {
			jQuery.extend(initial_sources, data.initial_sources);
		}
	);
};

$.fn.newElements = function() {
    // look for your inputs:
    this.find('input.my_base_autocomplete')
        // and in the event that it is the input, add ourself
        .andSelf()
        // filter the results to the ones you want
        .filter('#solution-formset input.my_base_autocomplete')
        // and attach your autocomplete:
        .autocomplete({
	    	source: function (request, response) {
				if (request.term.length < 2) {
					my_response_key = jQuery(this.element).closest('tr').attr('id');
					 response(initial_sources[my_response_key]);
				} else {
					// remote source
					$.getJSON('/solutionfixer/ingredient_autocomplete',
						request, function(data, status, xhr) {
							response(data);
					});
				}
			},
			minLength: 0,
			select: function(event,ui) {
				event.target.value = ui.item.label;
				jQuery(event.target).siblings('.my_base_hidden').val(ui.item.value)
				jQuery.post('/solutionfixer/process_baserm_bypk_update', 
					{
						solution_id: $(this).siblings('.solution_id').html(),
						baserm_id: ui.item.value
					},
					function (data) {
						// TODO change the outline, or icon or something to indicate
						// success?
				}, 'json');
				return false;
			}
	    }).focus(function() {
	        if (this.value == "") $(this).autocomplete('search');
	    });
};

function update_solution_percentage_multiple (solution_id, percentage) {
	jQuery.post('/solutionfixer/process_percentage_update',
		{
			solution_id: solution_id,
			percentage: percentage
		},
		function (data) {
			if (data.validation_message === undefined) {
				return false;
			} else {
				alert(data.validation_message);
			}
		
	}, 'json');
}

function update_solution_solvent(solution_id, solvent_id) {
	jQuery.post('/solutionfixer/process_solvent_update',
		{
			solution_id: solution_id,
			solvent_id: solvent_id
		},
		function (data) {
			return false;
	}, 'json');
}
var loadOnScroll = function() {
	if ($(window).scrollTop() > $(document).height() - ($(window).height()*3)) {
        // temporarily unhook the scroll event watcher so we don't call a bunch of times in a row
        $(window).unbind();
        // execute the load function below that will visit the JSON feed and stuff data into the HTML
        loadItems();
    }
};
var loadItems = function() {
	if(hasNextPage === false) {
		return false;
	}
	var checked_filters = jQuery('#filter-form input:checked');
	jQuery.ajax({
		url: '/solutionfixer/solution_loader',
		dataType: 'json',
		data: {
			last_index: jQuery('#solution-formset-tbody tr:last-child').attr('id'),
			show_unverified: jQuery("#id_status_0").attr('checked'),
			show_flagged: jQuery("#id_status_1").attr('checked'),
			show_verified: jQuery("#id_status_2").attr('checked')
		},
		success: function(data) {
			var new_row_ids = []; 
			var new_solution_ids = [];
			hasNextPage = data.hasNext;
			for(var i in data.rendered_rows) {
				var nextrow = $(data.rendered_rows[i]);
				if (jQuery("#id_status_0").attr('checked')) {
					// don't toggle them
				} else {
					if (jQuery(nextrow).hasClass('unverified')) {
						jQuery(nextrow).hide();
					}
				}
				if (jQuery("#tatus_1").attr('checked')) {
					// don't toggle them
				} else {
					if (jQuery(nextrow).hasClass('flagged')) {
						jQuery(nextrow).hide();
					}
				}
				if (jQuery("#id_status_2").attr('checked')) {
					// don't toggle them
				} else {
					if (jQuery(nextrow).hasClass('verified')) {
						jQuery(nextrow).hide();
					}
				}
			 	jQuery(nextrow).appendTo('#solution-formset-tbody').newElements();
				new_row_ids.push(nextrow.attr('id'));
				new_solution_ids.push(nextrow.find('span.solution_id').html());
			};
			$(this).getSuggestedResults(new_solution_ids, new_row_ids);
			if (jQuery('tbody>tr:visible').length == 0) {
				loadItems();
			}
		},
		complete: function(data, textStatus) {
			//jQuery('#solution-formset:last-child:nth-child(2):').
			jQuery(window).bind('scroll',loadOnScroll);
		}
	});
};

jQuery(document).ready(function(){
	
	$('body').append('<div id="ajaxBusy"><p><img src="/static/images/loading.gif"></p></div>');
	
	$('#ajaxBusy').css({
		display:"none",
		margin:"0px",
		paddingLeft:"0px",
		paddingRight:"0px",
		paddingTop:"0px",
		paddingBottom:"0px",
		position:"fixed",
		left:"5px",
		top:"65px",
		width:"auto"
	});

	$(this).getSuggestedResults(jQuery('#solution-formset-tbody .solution_id').map(function() {
									return this.innerHTML
								}).get(), 
								jQuery('#solution-formset-tbody tr').map(function() {
									return $(this).attr('id')
								}).get());
	$(this).newElements();

	jQuery("#filter-form").delegate('input', 'change', function (e) {
		var $this = $(this)[0];
		var status_value = $this.value;
		var my_selector = '#solution-formset-tbody>tr.' + status_value;
		if ($this.checked) {
			jQuery(my_selector).show();
		} else {
			jQuery(my_selector).hide();
		}
		if (jQuery('tbody>tr:visible').length == 0) {
			loadItems();
		}
	});
	
	jQuery("#solution-formset").delegate('select.status_selector', 'change', function (e) {
		var $this = $(this);
		var new_status = $this.children('option:selected')[0].innerHTML;
		var status_filtered = jQuery('#filter-form input:checked').map(function(){
			return this.value;
		});
		
		var my_status_id = 0;
		if (new_status == 'unverified') {
			my_status_id = 1;
		} else if (new_status == 'flagged'){
			my_status_id = 2;
		} else if (new_status == 'verified'){
			my_status_id = 3;
		} else if (new_status == 'unlisted'){
			my_status_id = 4;
		}

		jQuery.post('/solutionfixer/process_status_update',
			{
				solution_id: $this.closest('tr').children('td:nth-child(2)').children('input:first-child').val(),
				status_id: my_status_id
			},
			function (data) {
				if (data.validation_message == null) {
					$this.closest('tr').removeClass();
					$this.closest('tr').addClass(new_status);
					if (jQuery.inArray(new_status, status_filtered) != -1) {
						// stay shown
					} else {
						$this.closest('tr').toggle('highlight');
					}
				} else {
					$this.closest('tr').removeClass();
					$this.closest('tr').addClass('unverified');
					$this.val(1);
					alert(data.validation_message);
				}
		}, 'json');
	});
	
	jQuery('#solution-formset').delegate('input.percentage_input', 'keyup', function (e) {
		clearTimeout(t);
		var $this = $(this);
		var solution_id = $this.closest('tr').children('td:nth-child(2)').children('input:first-child').val();
		var percentage = $this.val();
		if (percentage == '') {
			percentage = -1;
		}
		t = setTimeout("update_solution_percentage_multiple(" + solution_id + ", " + percentage + ")", 750)
	});
		
	jQuery("#solution-formset").delegate('select.solvent_selector', 'change', function (e) {
		var $this = $(this)[0];
		
		var solution_id = $(this).closest('tr').children('td:nth-child(2)').children('input:first-child').val();
		var solvent_id =  $this.value;
		
		update_solution_solvent(solution_id, solvent_id);
	});
	
	jQuery("#solution-formset").delegate('select.solvent_selector', 'keyup', function (e) {
		update_solution_solvent($(this)[0]);
	});
	
	$(window).bind('scroll', loadOnScroll);
});

$(document).ajaxStart(function(){ 
  $('#ajaxBusy').show(); 
}).ajaxStop(function(){ 
  $('#ajaxBusy').hide();
});


// intial fiddle...we figured that the delegate to keyup of my code was the issue
//$("#myInput").autocomplete({
//    source: function( request, response ) {
//        if (request.term.length < 2) {
//            response(["aa","bb","cc","dd","ee","ff","gg"]);
//        } else {
//            $.ajax({
//                url: "http://ws.geonames.org/searchJSON",
//                dataType: "jsonp",
//                data: {
//                    featureClass: "P",
//                    style: "full",
//                    maxRows: 12,
//                    name_startsWith: request.term
//                },
//                success: function( data ) {
//                    response( $.map( data.geonames, function( item ) {
//                        return {
//                            label: item.name + (item.adminName1 ? ", " + item.adminName1 : "") + ", " + item.countryName,
//                            value: item.name
//                        }
//                    }));
//                }
//            });
//        }
//    },
//    minLength: 0
//}).focus(function(){
//    if (this.value == "")
//        $(this).trigger('keydown.autocomplete');
//});


