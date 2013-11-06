var TSRLI_ENTRY = {};

/*
function update_poli_row(row) {
	jQuery.get('/django/access/process_cell_update/', 
		{number: row.find('.pin-cell input').val(), amount: row.find('.quantity-cell input').val()},
		function (data) {
			row.children('.name-cell').html(data.name).end().children('.price-cell').html(data.cost);
			row.find("input[id$='raw_material']")[0].value=data.pk;
			
			if (data.name == 'Invalid Number') {
				row.addClass('invalid');
			} else {	
				jQuery('#po-submit-button').show();
				row.removeClass('invalid');
			}
			if(jQuery('.invalid').length == 0) {
				jQuery('#po-submit-button').show();
			} else {
				jQuery('#po-submit-button').hide();
			}
		}, 'json');	
};
*/

TSRLI_ENTRY.update_all_rows = function() {
	jQuery('#tsr-rows tr:gt(0)').each(function() {
		current_row = jQuery(this);
		TSRLI_ENTRY.update_tsrli_row(current_row);
		}
	);
};

TSRLI_ENTRY.update_tsrli_row = function(row) {
	jQuery.get('/django/access/process_tsrli_update/',
		{type: row.find(':checked').val(), number: row.find('.code-cell input').val()},
		function (data) {
			row.children('.name-cell').html(data.name).end();
			
		}, 'json');
};




jQuery(document).ready(function(){	
		
	/*jQuery('#poli-rows').delegate('input', 'keyup', function (e) {
		var $this = $(this);
		var row = $this.closest("tr");
		update_poli_row(row);
	});*/
	TSRLI_ENTRY.update_all_rows();
	
	jQuery('#tsr-rows input:radio').change( function() {
		var $this = $(this);
		var row = $this.closest("tr");
		TSRLI_ENTRY.update_tsrli_row(row);
	});
	
	jQuery('#tsr-rows').delegate('.code-cell input', 'keyup', function(e) {
		var $this = $(this);
		var row = $this.closest("tr");
		
		/*
		$this.autocomplete({
			source: '/django/access/ingredient_autocomplete',
			minLength: 1,
			select: function( event, ui ) {
				// ui.item.value is the item of interest
				row.find(".pin-cell input[id$='raw_material']").val( ui.item.value );
				update_poli_row(row);
			}
		*/
		console.log('hi');
		TSRLI_ENTRY.update_tsrli_row(row);
		
		});
	});