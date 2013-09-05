var FORMULA_EDIT ={};

function isNotEmpty(map) {  //I use this to check if FORMULA_EDIT is not empty
   for(var key in map) {
      if (map.hasOwnProperty(key)) {
         return true;
      }
   }
   return false;
}


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


function filter_rows() {
	remove_filter_messages();

	jQuery.get('/django/access/process_filter_update/',
		FORMULA_EDIT,
		function(data) {
			for (var key in data) {
				var index = jQuery('#formula-rows td.ingredient_pk-cell input').filter(function() { return jQuery(this).val() == key; }).closest("tr").index();
				jQuery('#formula-rows tr').eq(index-1).after(
					"<tr bgcolor='red'> <td colspan='5'> <b> The ingredient below doesn't meet the following filter categories: " + key + ":" + data[key] + " </b> </td> </tr>");
				jQuery('#formula-rows tr').eq(index).addClass('filter_message');
			}
		}, 'json');
}

function get_pks() {
	FORMULA_EDIT.pks = [];
	
	jQuery("#formula-rows tr.formula_row").each(function () { //GET THE PK OF ALL ROWS WITH CLASS FORMULA_ROW 
		
		row_pk = jQuery(this).find('td.ingredient_pk-cell input').val();
		FORMULA_EDIT.pks.push(row_pk);
	});
	
}



function remove_filter_messages() {
	var message_rows = jQuery("#formula-rows tr.filter_message");
	message_rows.remove();
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
	get_pks();
	get_checked_boxes();
	filter_rows();
}

jQuery(document).ready(function(){	

	jQuery('#formulaedit-filterselect input:checkbox').change( function() {

		
		get_checked_boxes();
		get_pks();
			
		console.log("Art/nat: " + FORMULA_EDIT.checked_boxes["art_nati"]);
		//console.log("Allergens: " + allergen);
		console.log("Prop65: " + FORMULA_EDIT.checked_boxes["prop65"]);
	
		filter_rows();

		
	});
	
	if(jQuery("#formula-rows").length > 0) {
		jQuery(document).ready(function() {
			console.log("The page has just been refreshed");
			get_checked_boxes();
			get_pks();
			filter_rows();
		});
	}
});