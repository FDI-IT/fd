var FORMULA_EDIT = {};

function get_checked_boxes() { 
	FORMULA_EDIT.checked_boxes = {};
	var checkboxes = jQuery('#formulaedit-filterselect input:checkbox:checked');
	
	for(var i = 0; i < checkboxes.length; i++) {
		var my_box = checkboxes[i];
		
		if ( my_box.name in FORMULA_EDIT.checked_boxes ) {
			FORMULA_EDIT.checked_boxes[my_box.name].push(my_box.value);
		} else {
			FORMULA_EDIT.checked_boxes[my_box.name] = [my_box.value];
		}
	}
}
function validate_all_rows() {
	var invalid = false;
	
	jQuery('#formula-rows tr:gt(0)').each(function() {
		if(jQuery(this).find('.name-cell').html() == 'Invalid Ingredient Number') {
			jQuery(this).addClass('invalid_number');
			invalid = true;
		}
		if(isNaN(jQuery(this).find('.amount-cell input').val())) {
			jQuery(this).addClass('invalid_amount');
			invalid = true;
		}
		jQuery(this).find('input').each(function() {
			if(jQuery(this).val() == '') {
				var currentRow = jQuery(this).closest('tr');
				currentRow.addClass('empty');
				invalid = true;
			}
		});

	});

	if (invalid) {
		return false;
	}
	else {
		return true;
	}	
} 


function remove_filters() {
	jQuery('#formula-rows tr').removeAttr('title'); //the title attribute adds a tooltip
	jQuery('#formula-rows tr').attr('class', 'formula_row');
	jQuery('#formula-rows tr').css('background-color','white');
}	


function add_error_messages() {
	jQuery('#formula-rows tr').each(function() {
		var error_message = [];
		if (jQuery(this).hasClass('invalid_number') || jQuery(this).hasClass('empty') || jQuery(this).hasClass('invalid_amount')){
			if (jQuery(this).hasClass('invalid_number')) {
				error_message.push("Invalid ingredient number");
			}
			if (jQuery(this).hasClass('empty')) {
				error_message.push("Empty field(s)");
			}
			if (jQuery(this).hasClass('invalid_amount')) {
				error_message.push("Invalid amount");
			}
			jQuery(this).attr("title", "Please fix the following error(s): " + error_message.join(", "));
			jQuery(this).css('background-color', '#FF0000');
		}
	});
}


function filter_rows() {
	
	jQuery.get('/django/access/process_filter_update/',
		FORMULA_EDIT,
		function(data) {
			for (var key in data) {
				var index = jQuery('#formula-rows td.ingredient_pk-cell input').filter(function() { return jQuery(this).val() == key; }).closest("tr").index();
				var filter_row = jQuery('#formula-rows tr').eq(index);
				filter_row.addClass('filter_row');
				filter_row.attr("title", "This ingredient does not meet the following filters: " + data[key]);
				jQuery('#formula-rows tr.filter_row').css('background-color','#FF6666');
			}
			add_error_messages();
			toggle_submit();
			
		}, 'json');
	
}

function get_pks() {
	FORMULA_EDIT.pks = [];
	
	jQuery("#formula-rows tr.formula_row:gt(0)").each(function () { //GET THE PK OF ALL ROWS WITH CLASS FORMULA_ROW 
		
		row_pk = jQuery(this).find('td.ingredient_pk-cell input').val();
		if(row_pk != "")
			FORMULA_EDIT.pks.push(row_pk);
	});
	
}

//obtain pk at given row
//jQuery(this).children('.ingredient_pk-cell').children('input').val()

//change pk at given row
//jQuery(row).children('.ingredient_pk-cell').children('input').attr("value","86")

//insert row at given index:
//jQuery('#formula-rows tr').eq(index).after(html);
//$('#my_table > tbody > tr').eq(i-1).after(html);


//get the row where pk = 492
//var row = jQuery('#formula-rows td.ingredient_pk-cell input').filter(function() { return jQuery(this).val() == 492; }).closest("tr");

//obtain the index of the row where pk = 722
//jQuery('#formula-rows td.ingredient_pk-cell input').filter(function() { return jQuery(this).val() == 722; }).closest("tr").index();

function filter_update() {
	
	remove_filters();
	//number_validation();
	//amount_validation();
	//fields_are_not_empty();
	validate_all_rows();
	get_pks();
	get_checked_boxes();
	filter_rows();
	
}



function update_all_formula_rows () {
	var first = true;
	jQuery('#formula-rows tr').each( function() {
		if (first == true) {
			first = false;
		} else {
			update_formula_row(jQuery(this));
		}
	});
}

function toggle_submit () {
	if(validate_all_rows()) {
		jQuery('#formula-submit-button').show();
	}
	else {
		jQuery('#formula-submit-button').hide();
	}
	
	//add_error_messages();
}

function update_formula_row (row) {
	clearTimeout(t);	
	
	jQuery.get('/django/access/process_cell_update/', 
		{
		    number: row.find('.number-cell input').val(), 
		    amount: row.find('.amount-cell input').val()
		},
		function (data) {
			row.children('.name-cell').html(data.name).end().children('.cost-cell').html(data.cost);
			jQuery(row).children('.ingredient_pk-cell').children('input').attr("value", data.pk);
			
			if (data.name == 'Invalid Ingredient Number') {
				row.addClass('invalid_number');
			} else {	
				FORMULA_EDIT.t = setTimeout("recalculate_total_cost()", 750);
				//FORMULA_EDIT.t2 = setTimeout("filter_update()", 750);
				row.removeClass('invalid_number');
			}
			FORMULA_EDIT.invalid_number_rows = jQuery('.invalid_number').length;
			//filter_update();
		}, 'json');	
}


function delete_row(i){
	document.getElementById('formula-rows').deleteRow(i);
	var form_id = $('#id_form-TOTAL_FORMS').val();
	jQuery('#id_form-TOTAL_FORMS').val(Number(form_id)-1);
	var value_to_decrement = i;
	jQuery('#formula-rows tr').each(
		function(index, value){
			if (i - 1 < index ) {
				jQuery(value).find('input[type="text"]').each(
					function( input_index, input_value) {
						var my_name = jQuery(input_value).attr('name');
						var new_name = my_name.replace(value_to_decrement, value_to_decrement-1);
						jQuery(input_value).attr('name', new_name);
						var my_id = jQuery(input_value).attr('id');
						var new_id = my_id.replace(value_to_decrement, value_to_decrement-1)
						jQuery(input_value).attr('id', new_id);
			
				});
				value_to_decrement += 1;
			}
	});
	
	filter_update();
};

function normalize_weight () {
	var sum=0;
	jQuery('.amount-cell input').each( function() {
		sum = sum + parseFloat(this.value);
	});
	var correction_factor = 1000.0 / sum;
	if(isNaN(correction_factor)) {
		alert("Please enter a valid number in all the amount cells.");
	} else {
		jQuery('.amount-cell input').each( function() {
			this.value = Math.round(this.value * correction_factor * 1000) / 1000;
		});
		update_all_formula_rows();
		recalculate_total_cost();
	}
	
	return false;
}

function recalculate_total_cost() {
	var total_cost = 0;
	var total_weight = 0;
	jQuery('.cost-cell').each(function() {
		total_cost += Number($(this).html());
	});
	total_cost = Math.round(total_cost*1000)/1000;
	jQuery("#RawMaterialCost").html(total_cost);
	
	jQuery('.amount-cell').each(function() {
		total_weight += Number($(this).find('input').val());
	});
	total_weight = Math.round(total_weight*1000)/1000;
	jQuery("#FormulaWeight").html(total_weight);
};

jQuery(document).ready(function(){	

	if(jQuery("#formula-rows").length > 0) {
		jQuery(document).ready(function() {
			console.log("The page has just been refreshed");
			$('input:checkbox').removeAttr('checked');
			update_all_formula_rows();
			filter_update();
		});
	}

	jQuery('#formulaedit-filterselect input:checkbox').change( function() {
		filter_update();
	});
	
	
	jQuery('#formula-rows').delegate('input', 'keyup', function (e) {
		var $this = $(this);
		var row = $this.closest("tr");
		update_formula_row(row);
		FORMULA_EDIT.t2 = setTimeout("filter_update()", 750);
	});	
	
	jQuery('#formula-rows').delegate('.number-cell input', 'keyup', function(e) {
		var $this = $(this);
		var row = $this.closest("tr");
		//update_formula_row(row);
		$this.autocomplete({
			source: '/django/access/ingredient_autocomplete',
			minLength: 1,
			select: function( event, ui ) {
				// ui.item.value is the item of interest
				row.find('.number-cell input').val( ui.item.value );
				update_formula_row(row);
				filter_update();
			}
		});
	});


	jQuery('#add-formula-row-button').click(function(){
		var form_id = $('#id_form-TOTAL_FORMS').val();
		jQuery('#id_form-TOTAL_FORMS').val(Number(form_id)+1);
		
		jQuery('#formula-rows tr:last').after(
			'<tr class="formula_row">' + 
			'<td class="number-cell"><input type="text" name="form-' + form_id + '-ingredient_number" id="id_form-' + form_id + '-ingredient_number" /></td>' +
			'<td class="amount-cell"><input type="text" name="form-' + form_id + '-amount" id="id_form-' + form_id + '-amount" /></td>' +
			'<td class="name-cell"></td>' +
			'<td class="cost-cell"></td>' +
			'<td class="ingredient_pk-cell" style="display:none"> <input type="text"> </td>' +
			'<td class="del-row"><input type="button" value="X" onclick="delete_row(this.parentNode.parentNode.rowIndex)"></td>' +
			'</tr>');
		jQuery('#id_form-' + form_id + '-ingredient_number').focus();
		filter_update();
		return false;
	});	



	jQuery('#solution-ingredient-autocomplete').delegate('input', 'keyup', function(e) {
		var $this = $(this);
//		var row = $this.closest("tr");
		$this.autocomplete({
			source: '/django/access/ingredient_autocomplete',
			minLength: 1,
			select: function( event, ui ) {
				jQuery.post('/django/solutionfixer/process_baserm_update', 
					{
						solution_id: jQuery('#solution_id').html(),
						baserm_id: ui.item.value
					},
					function (data) {
						// ui.item.value is the item of interest
						$this.val( ui.item.value );
						jQuery("#solution-baserm").html(ui.item.label);
						//update_formula_row(row);
						return false;
				}, 'json');
			}
		});
	});
	
		
	// begin solution label code
	// TODO this is essentially a repeat of the above which means some stuff needs 
	// to be refactored. The only difference is the selectors, because the markup
	// is not consistent between two views.
	// which two views? formula edit, and solution label generator
	jQuery('#solution-form').delegate('input,select', 'change', function (e) {
		clearTimeout(t);
		t = setTimeout("update_label_preview()", 750);
	});

	jQuery("#id_ingredient_picker").autocomplete({
		source: '/django/access/ingredient_autocomplete/',
		minLength: 1,
		select: function(event, ui) {
				jQuery.get('/django/lab/ingredient_label',
					{ingredient_id:ui.item.value},
					function (data) {
						jQuery("#id_pin").val(ui.item.value);
						jQuery("#id_nat_art").val(data.nat_art);
						jQuery("#id_pf").val(data.pf);
						jQuery("#id_product_name").val(data.product_name);
						jQuery("#id_product_name_two").val(data.product_name_two);
						update_label_preview();
					}, 'json');
			}
	});
	// end solution label js
	// begin experimental label js
	
	jQuery('#new_solution_form #id_ingredient').autocomplete({
		source: '/django/access/ingredient_autocomplete/',
		minLength: 1,
		select: function(event, ui) {
			console.log(ui.item.value);
		}
	});
	
});