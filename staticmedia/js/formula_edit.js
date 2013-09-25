var FORMULA_EDIT = {};

FORMULA_EDIT.get_checked_boxes = function() { 
	FORMULA_EDIT.checked_boxes = {};
	
	jQuery('#formulaedit-filterselect input:checkbox:checked').each( function() {
		if ( this.name in FORMULA_EDIT.checked_boxes ) {
			FORMULA_EDIT.checked_boxes[this.name].push(this.value);
		} else {
			FORMULA_EDIT.checked_boxes[this.name] = [this.value];
		}
	});
};

FORMULA_EDIT.validate_row = function(row) {
	var invalid = false;

	var row = jQuery(row);
	
	if(row.find('.name-cell').html() == "") {
		row.addClass('invalid_number');
		invalid = true;
	}
	if(isNaN(row.find('.amount-cell input').val())) {
		row.addClass('invalid_amount');
		invalid = true;
	}
	row.find('input').each(function() {
		var $this = jQuery(this);
		if($this.val() == '') {
			var currentRow = $this.closest('tr');
			currentRow.addClass('empty');
			invalid = true;
		}
	});
	
	if (invalid) {
		return false;
	}
	else {
		return true;
	}
};

FORMULA_EDIT.validate_all_rows = function () {
	var invalid = false;
	
	jQuery('#formula-rows tr:gt(0)').each(function() {
		if(FORMULA_EDIT.validate_row(this) == false) {
			invalid = true;
		}
	});

	if (invalid) {
		return false;
	}
	else {
		return true;
	}	
};

FORMULA_EDIT.remove_row_filter = function(row) {
	FORMULA_EDIT.remove_filter_for_object(jQuery(row));
};

FORMULA_EDIT.remove_all_filters = function() {
	FORMULA_EDIT.remove_filter_for_object(jQuery('#formula-rows tr'));
};

FORMULA_EDIT.remove_filter_for_object = function(jquery_object) {
	
	jquery_object.removeAttr('title')
			   .attr('class', 'formula_row')
			   .css('background-color','white');
};

FORMULA_EDIT.add_row_error_messages = function(row) {
	var error_message = [];
	row = jQuery(row);

	if (row.hasClass('invalid_number')) {
		error_message.push("Invalid ingredient number");
	}
	if (row.hasClass('empty')) {
		error_message.push("Empty field(s)");
	}
	if (row.hasClass('invalid_amount')) {
		error_message.push("Invalid amount");
	}
	if (error_message.length > 0) {
		row.attr("title", "Please fix the following error(s): " + error_message.join(", "));
		row.css('background-color', '#FF0000');
	}
	
};

FORMULA_EDIT.add_all_error_messages = function() {
	jQuery('#formula-rows tr').each(function() {
		FORMULA_EDIT.add_row_error_messages(this);
	});
};

FORMULA_EDIT.filter_single_row = function(row) {
	jQuery.get('/django/access/process_filter_update/',
		{
			pks: FORMULA_EDIT.pks,
			checked_boxes: FORMULA_EDIT.checked_boxes,
			invalid_number_rows: FORMULA_EDIT.invalid_number_rows,
		},
		function(data) {
			
			row_pk = jQuery(row).children('.ingredient_pk-cell').children('input').val();

			if (row_pk in data) {
				row.addClass('filter_row')
	          			  .attr("title", "This ingredient does not meet the following filters: " + data[row_pk]);	
	          	
	          	jQuery(row).css('background-color', '#FF6666');
			}
			

			FORMULA_EDIT.add_row_error_messages(row);
			FORMULA_EDIT.toggle_submit();
			
		}, 'json');
	
};

FORMULA_EDIT.filter_all_rows = function() {
	jQuery.get('/django/access/process_filter_update/',
		{
			pks: FORMULA_EDIT.pks,
			checked_boxes: FORMULA_EDIT.checked_boxes,
			invalid_number_rows: FORMULA_EDIT.invalid_number_rows,
		},
		function(data) {
			for (var key in data) {
				// this weird filter is to select inputs by value with a variable
				var filter_row = jQuery('#formula-rows td.ingredient_pk-cell input').filter(function() { return jQuery(this).val() == key; }).closest("tr");
				filter_row.addClass('filter_row')
				          .attr("title", "This ingredient does not meet the following filters: " + data[key]);
				
			}
			jQuery('#formula-rows tr.filter_row').css('background-color','#FF6666');
			FORMULA_EDIT.add_all_error_messages();
			FORMULA_EDIT.toggle_submit();
			
		}, 'json');
	
};

FORMULA_EDIT.get_pks = function () {
	FORMULA_EDIT.pks = [];
	
	jQuery("#formula-rows tr.formula_row:gt(0)").each(function () { //GET THE PK OF ALL ROWS WITH CLASS FORMULA_ROW 
		
		row_pk = jQuery(this).find('td.ingredient_pk-cell input').val();
		if(row_pk != "")
			FORMULA_EDIT.pks.push(row_pk);
	});
	
};

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

FORMULA_EDIT.filter_update_all = function() {
	
	FORMULA_EDIT.remove_all_filters();
	FORMULA_EDIT.validate_all_rows();
	FORMULA_EDIT.get_pks();
	FORMULA_EDIT.get_checked_boxes();
	FORMULA_EDIT.filter_all_rows();
	
};

FORMULA_EDIT.filter_update_row = function(row) {
	FORMULA_EDIT.remove_row_filter(row);
	FORMULA_EDIT.validate_row(row);
	FORMULA_EDIT.get_pks();
	FORMULA_EDIT.get_checked_boxes();
	FORMULA_EDIT.filter_single_row(row);
};


FORMULA_EDIT.toggle_submit = function() {
	if(FORMULA_EDIT.validate_all_rows() && jQuery("#formula-rows tr.filter_row").length == 0) {
		jQuery('#formula-submit-button').show();
	}
	else {
		jQuery('#formula-submit-button').hide();
	}
	
	//FORMULA_EDIT.add_all_error_messages();
};

FORMULA_EDIT.update_formula_row = function(row) {
	clearTimeout(FORMULA_EDIT.t);	
	
	jQuery.get('/django/access/process_cell_update/', 
		{
		    number: row.find('.number-cell input').val(), 
		    amount: row.find('.amount-cell input').val()
		},
		function (data) {
			if (data.name == 'Invalid Ingredient Number') {
				row.children('.name-cell').html("");
				row.addClass('invalid_number');
			} else {	
				row.children('.name-cell').html(data.name).end().children('.cost-cell').html(data.cost);
				jQuery(row).children('.ingredient_pk-cell').children('input').attr("value", data.pk);
				FORMULA_EDIT.t = setTimeout("FORMULA_EDIT.recalculate_total_cost()", 750);
				//FORMULA_EDIT.t2 = setTimeout("FORMULA_EDIT.filter_update_all()", 750);
				row.removeClass('invalid_number');
			}
			FORMULA_EDIT.invalid_number_rows = jQuery('.invalid_number').length;
			//FORMULA_EDIT.filter_update_all();
		}, 'json');	
};

FORMULA_EDIT.update_all_formula_rows = function() {
	jQuery('#formula-rows tr:gt(0)').each( function() {
		FORMULA_EDIT.update_formula_row(jQuery(this));
	});
};

FORMULA_EDIT.delete_row = function(i){
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
	
	FORMULA_EDIT.filter_update_all();
};

FORMULA_EDIT.recalculate_total_cost= function() {
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

FORMULA_EDIT.normalize_weight = function() {
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
		FORMULA_EDIT.update_all_formula_rows();
		FORMULA_EDIT.recalculate_total_cost();
	}
	
	return false;
};

jQuery(document).ready(function(){	

	if(jQuery("#formula-rows").length > 0) {
		jQuery(document).ready(function() {
			$('input:checkbox').removeAttr('checked');
			FORMULA_EDIT.update_all_formula_rows();
			FORMULA_EDIT.filter_update_all();
		});
	}

	jQuery('#formulaedit-filterselect input:checkbox').change( function() {
		FORMULA_EDIT.filter_update_all();
	});
	
	
	jQuery('#formula-rows').delegate('input', 'keyup', function (e) {
		var $this = $(this);
		var row = $this.closest("tr");
		FORMULA_EDIT.update_formula_row(row);
		//FORMULA_EDIT.t2 = setTimeout("FORMULA_EDIT.filter_update_all()", 750);
		FORMULA_EDIT.t2 = setTimeout(function() {
					FORMULA_EDIT.filter_update_row(row);
				}, 750);
	});	
	
	jQuery('#formula-rows').delegate('.number-cell input', 'keyup', function(e) {
		var $this = $(this);
		var row = $this.closest("tr");
		//FORMULA_EDIT.update_formula_row(row);
		$this.autocomplete({
			source: '/django/access/ingredient_autocomplete',
			minLength: 1,
			select: function( event, ui ) {
				// ui.item.value is the item of interest
				row.find('.number-cell input').val( ui.item.value );
				FORMULA_EDIT.update_formula_row(row);
				
				//need timeout to ensure that new pk is in FORMULA_EDIT before filtering the row
				FORMULA_EDIT.t2 = setTimeout(function() {
					FORMULA_EDIT.filter_update_row(row);
				}, 750);
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
			'<td class="del-row"><input type="button" value="X" onclick="FORMULA_EDIT.delete_row(this.parentNode.parentNode.rowIndex)"></td>' +
			'</tr>');
		jQuery('#id_form-' + form_id + '-ingredient_number').focus();
		FORMULA_EDIT.filter_update_row(jQuery('#formula-rows tr:last'));
		return false;
	});	
	
});