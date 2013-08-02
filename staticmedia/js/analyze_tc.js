jQuery(document).ready(function() {
	var progress_steps = jQuery('#progress-steps li');
	var i = 0;
	var process_next_card = function(){
		jQuery.post('/django/qc/analyze_scanned_cards/', 
			[null], 
			function(data){
				jQuery(progress_steps[i]).removeClass('active').addClass('complete');
				i += 1;
				jQuery(progress_steps[i]).addClass('active');
				jQuery('#content-solo').append(data.preview);
				if (data.fail == 'fail') {
					jQuery('#loading').hide();
					jQuery('#done').removeClass('hidden');
				}
				else {
					process_next_card();
				};
			});
	};
	process_next_card();
});
