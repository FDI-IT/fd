jQuery.get('/django/solutionfixer/get_match_guesses',
		{
			solution_ids: jQuery('#solution-formset-tbody .solution_id').map(function() {
									return this.innerHTML
								}).get(),
			row_ids: jQuery('#solution-formset-tbody tr').map(function() {
									return $(this).attr('id')
								}).get()
		},
		function (data) {
			jQuery.extend(initial_sources, data.initial_sources);
		}
	);