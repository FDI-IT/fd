
jQuery(document).ready(function(){	
	$( "#reports_experimental_log_details" ).tablesorter({
			headers: {
			0: {
				sorter: 'text'
			},
			1: {
				sorter: 'link-digit'
			},
			2: {
				sorter: 'link-digit'
			},
			3: {
				sorter: 'text'
			},
			4: {
				sorter: 'text'
			},
			5: {
				sorter: 'shortDate'
			},
			6: {
				sorter: 'link-digit'
			},
			7: {
				sorter: 'digit'
			},
			8: {
				sorter: 'digit'
			},
			9: {
				sorter: 'digit'
			},
			10: {
				sorter: 'digit'
			},
			11: {
				sorter: 'digit'
			},
			12: {
				sorter: 'digit'
			},
			13: {
				sorter: 'digit'
			},
			14: {
				sorter: 'digit'
			}
	}});
	
	jQuery("#reports_experimental_log_details :checkbox").change( function(){
		var my_tr = jQuery(this).closest('tr');
		var my_checked = this.checked;
		jQuery.post('/reports/experimental_log_exclude/',
			{
				epk: this.value,
				exclude_from_reporting: this.checked,
				csrfmiddlewaretoken: jQuery('input[name="csrfmiddlewaretoken"]')[0].value
			},
			function (data) {
				if (my_checked) {
					my_tr.addClass('reports_exclude');
				} else {
					my_tr.removeClass('reports_exclude');
				}
		}, 'json');
	});
});
