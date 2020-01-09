update_ingredient_name = function(row) {
    //	clearTimeout(FORMULA_EDIT.t);

	jQuery.get('/access/ingredient/get_ingredient_name/',
		{
		    pin: row.find('.pin-field input').val()
		},
		function (data) {
			if (data.name == 'Invalid Ingredient Number') {
				row.children('.name-field').html("Invalid PIN");
				row.addClass('invalid_number');
			} else {
				row.children('.name-field').html(data.name);
				row.removeClass('invalid_number');
			}
		}, 'json');
};

jQuery(document).ready(function() {

	jQuery('.entry-row').on('keyup','.pin-field input', function() {
		var $this = $(this);
		console.log($this)
		var row = $this.closest("tr");
		console.log(row);

        update_ingredient_name(row);

	});

});