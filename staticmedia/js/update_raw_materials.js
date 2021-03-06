

jQuery(document).ready(function(){
	
	var row = jQuery('#rm-by-code input[name=activate]:checked').closest('tr');
	
	if(jQuery(row).hasClass("active")) {
		jQuery('#update-submit-button').attr('disabled', true).attr('title', 'Activate a discontinued raw material above to update.');
	}
	

	
	$("input[name='activate']").change(function(){
		var row = jQuery('#rm-by-code input[name=activate]:checked').closest('tr');
		
		if(jQuery(row).hasClass("active")) {
			jQuery('#update-submit-button').attr('disabled', true).attr('title', 'Activate a discontinued raw material above to update.');
		}
		else {
			jQuery('#update-submit-button').attr('disabled', false).removeAttr('title');
		}
	});
	
	jQuery('#update-submit-button').click(function(){
		var row = jQuery('#rm-by-code input[name=activate]:checked').closest('tr');
		var rm_code = jQuery(row).find('.rm_code').text();
		// var rm_id = jQuery("#rm_id").text();
		
		if(rm_code == "") {
			var ingredient_id = jQuery(row).find('.ingredient_id-cell').text();
			rm_code = "discontinue_all/" + ingredient_id;
		}
		
		console.log(rm_code);
		
		
		window.location.href = "/access/ingredient/activate/" + rm_code + "/";
	});

});