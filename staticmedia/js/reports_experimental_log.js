
jQuery(document).ready(function(){	
	jQuery("#reports_experimental_log_details :checkbox").change( function(){
		var my_tr = jQuery(this).closest('tr');
		var my_checked = this.checked;
		jQuery.post('/django/reports/experimental_log_exclude/',
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
