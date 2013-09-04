// this variable designates a timeout to recalculate the total cost
var t;

var FORMULA_FILTER ={};

function isNotEmpty(map) {  //I use this to check if FORMULA_FILTER is not empty
   for(var key in map) {
      if (map.hasOwnProperty(key)) {
         return true;
      }
   }
   return false;
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

function get_checked_boxes() { 
	FORMULA_FILTER.checked_boxes = {};
	var checkboxes = jQuery('#formulaedit-filterselect input:checkbox:checked');
	
	for(var i = 0; i < checkboxes.length; i++) {
		var my_box = checkboxes[i];
		
		if ( my_box.name in FORMULA_FILTER.checked_boxes ) {
			FORMULA_FILTER.checked_boxes[my_box.name].push(my_box.value);
		} else {
			FORMULA_FILTER.checked_boxes[my_box.name] = [my_box.value];
		}
	}
}

function get_pks() {
	FORMULA_FILTER.pks = [];
	
	jQuery("#formula-rows tr.formula_row").each(function () { //GET THE PK OF ALL ROWS WITH CLASS FORMULA_ROW 
		
		row_pk = jQuery(this).find('td.ingredient_pk-cell input').val();
		FORMULA_FILTER.pks.push(row_pk);
	});
}



function remove_filter_messages() {
	var message_rows = jQuery("#formula-rows tr.filter_message");
	message_rows.remove();
}

function remove_extra_rows() {
	while (jQuery("#formula-rows tr").filter(":last").hasClass('formula_row') == false)
		jQuery("#formula-rows tr").filter(":last").remove()
}

function remove_duplicate_messages() {
	var seen = {};
	jQuery('#formula-rows tr.filter_message').each(function() {
	    var txt = jQuery(this).children('.filter_message_pk').text();
	    if (seen[txt])
	        jQuery(this).remove();
	    else
	        seen[txt] = true;
	});
}

function filter_rows() {
	jQuery('#formula-submit-button').show();
	remove_filter_messages();

	jQuery.get('/django/access/process_filter_update/',
		FORMULA_FILTER,
		function(data) {
			for (var key in data) {
				var index = jQuery('#formula-rows td.ingredient_pk-cell input').filter(function() { return jQuery(this).val() == key; }).closest("tr").index();
				jQuery('#formula-rows tr').eq(index-1).after(
					"<tr bgcolor='red'> <td colspan='5'> <b> The ingredient below doesn't meet the following filters: " + key + ":" + data[key] + " </b> </td>" +
						"<td class='filter_message_pk' style='display:none'>" + key + "</td> </tr>");
				jQuery('#formula-rows tr').eq(index).addClass('filter_message');
				jQuery('#formula-submit-button').hide();
			}
		}, 'json');
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
	remove_extra_rows();
	remove_duplicate_messages();
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
			jQuery(row).children('.ingredient_pk-cell').children('input').attr("value", data.pk)
			
			if (data.name == 'Invalid Number') {
				row.addClass('invalid');
			} else {	
				t = setTimeout("recalculate_total_cost()", 750);
				t2 = setTimeout("filter_update()", 750);
				jQuery('#formula-submit-button').show();
				row.removeClass('invalid');
			}
			if(jQuery('.invalid').length == 0 && jQuery('.filter_message').length == 0) {
				jQuery('#formula-submit-button').show();
			} else {
				jQuery('#formula-submit-button').hide();
			}
		}, 'json');	

}



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

function update_solution_percentage () {
	jQuery.post('/django/solutionfixer/process_percentage_update',
		{
			solution_id: jQuery('#solution_id').html(),
			percentage: jQuery('#matchform input[name=percentage]')[0].value
		},
		function (data) {
			if (data.validation_message === undefined) {
				jQuery("#status-message").html("");
			} else {
				jQuery("#status-message").html("<h1>" + data.validation_message + "</h1>");
			}
		
	}, 'json');
}

function adjust_weight(f) {
	var actual_adjusted_weight = jQuery(f).children('input[name="wf"]')[0].value;
	var weight_factor = actual_adjusted_weight / 1000;
	jQuery(f).parent().siblings('table').find('tbody > tr').each( function(i,tr) {
		tr.cells[4].innerHTML = (tr.getAttribute("data-ogw") * weight_factor).toFixed(3);
	});
	jQuery('#actual_adjusted_weight')[0].value= actual_adjusted_weight;
	return false;	
}
function adjust_weight_explosion(f) {
	var weight_factor = jQuery(f).children('input[name="wf"]')[0].value / 1000;
	jQuery(f).parent().siblings('div.ft-formula').find('span.ftamount').each( function(i,ftamount) {
		ftamount.innerHTML = (ftamount.getAttribute("data-ogw") * weight_factor).toFixed(3);
	});
	
	return false;	
}


function hideftrow(elem) {
	jQuery(elem).parent().parent().next().toggle();
}

function ft_collapse_all() {
	jQuery('div.ft-spacer').hide();
}

function ft_expand_all() {
	jQuery('div.ft-spacer').show();
}


// Parses URL parameters and puts them here so that js can easily read it.
var urlParams = {};
(function () {
    var e,
        a = /\+/g,  // Regex for replacing addition symbol with a space
        r = /([^&;=]+)=?([^&;]*)/g,
        d = function (s) { return decodeURIComponent(s.replace(a, " ")); },
        q = window.location.search.substring(1);

    while (e = r.exec(q))
       urlParams[d(e[1])] = d(e[2]);
})();

function getParameterByName(url, name) {

    var match = RegExp('[?&]' + name + '=([^&]*)')
                    .exec(url);

    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));

}

function search_results_popup() {
	newwindow = popup_window('/django/mysearch/print/' + window.location.search);
	newwindow.onload = function (e) {
		newwindow.print();
	}
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
};

function sortwithcolor_lineitem( column ) {
	$("#sales-order-by-lineitem tr").heatcolor(
		function() {
			var number = $("td:nth-child(9)", this).text();
			return number; 
		},
		{
			colorStyle: 'greentored',
			minval: 0,
			maxval: 3.5
		}
	);
};

function toggle_visible(){
	var ele = document.getElementById("advanced-search");
	var txt = document.getElementById("showhidetoggle");
	if (ele.style.display == "block") {
		txt.innerHTML = "Show search options";
	} else {
		txt.innerHTML = "Hide search options";
	}
	jQuery(ele).toggle();
}

function sortplain(column){
	$("#sales-order-by-lineitem tr").attr('style','background-color: rgb(255,255,255);');
};

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



function ajax_retain_status_change( new_status ) {
	var STATUS_INDEX;
	var page_title = jQuery('h2')[0].innerHTML;
	if (page_title == "RM Retains") {
		STATUS_INDEX = 8;
	} else {
		STATUS_INDEX = 6;	
	}	
	jQuery('td').removeClass('highlight');
	var value_list = [];
	jQuery('form[name="retain_selections"]').find(':checked').each( function(i,e) {
		value_list.push(e.value)
	});
	jQuery.post('/django/qc/ajax_retain_status_change/',
			{
				new_status: new_status,
				retain_list: value_list.join("|"),
				csrfmiddlewaretoken: jQuery('input[name="csrfmiddlewaretoken"]')[0].value,
			},
			function () {
				for (var i=value_list.length-1;i>=0; --i) {
					var mycells = jQuery('input[value="'+value_list[i]+'"]').parent().parent().children().addClass('highlight');
					jQuery(mycells[STATUS_INDEX]).html('<a href="/django/qc/rm_retains/' + new_status+ '/">' + new_status + '</a>');
				}
		}, 'json');
}

function update_label_preview () {
//	jQuery("#id_nat_art").val(data.nat_art);
//						jQuery("#id_pf").val(data.pf);
//						jQuery("#id_product_name").val(data.product_name);
//						jQuery("#id_product_name_two").val(data.product_name_two);
	var pin = jQuery("#id_pin").val();
	var nat_art = jQuery("#id_nat_art").val();
	var pf = jQuery("#id_pf").val();
	var product_name = jQuery("#id_product_name").val();
	var product_name_two = jQuery("#id_product_name_two").val();
	var concentration = jQuery("#id_concentration").val();
	var solvent = jQuery("#id_solvent").val();
	jQuery.get('/django/lab/solution',
		{
			preview:true,
			pin:pin,
			nat_art:nat_art,
			pf:pf,
			product_name:product_name,
			product_name_two:product_name_two,
			pin:pin,
			concentration:concentration,
			solvent:solvent
		},
		function (data) {
			d = new Date();
			jQuery('#label-preview').attr('src', '/djangomedia/images/preview.png?'+d.getTime());
		}, 'json');
};

jQuery(document).ready(function(){	

	
	$('table.sorttable').tablesorter();
	
	// change this so that it first checks if the right div has
	// been loaded, and if it is loaded, recall it. save the old div
	// so that it can be recalled later.
	// also add a loading animation.
	// the request doesn't work quite right, there's an extra
	// unexplained dereference in ft_review_table.py
	// $('#related-links a[href*="ajax"]').click(function(e) {
		// jQuery('div.ajax-content-table > div').hide();
		// jQuery.get(
			// e.target,
			// {},
			// function(data) {
				// jQuery('div.ajax-content-table').append(data);
			// }, 'html');
		// return false;
	// });
	
	//$('body').append('<div id="ajaxBusy"><p><img src="/djangomedia/images/loading.gif"></p></div>');
	$('#ajaxBusy').css({
		display:"none",
		margin:"0px",
		paddingLeft:"0px",
		paddingRight:"0px",
		paddingTop:"0px",
		paddingBottom:"0px",
		position:"fixed",
		left:"5px",
		top:"65px",
		width:"auto"
	});
	
	
	try {
		jQuery('#adjusted_weight').val(urlParams['wf']);
	} catch(err) {
		
	}
	
	jQuery("#select_all").click( function(){
		jQuery(':checkbox').prop("checked", true);
		return false;
	});
	jQuery("#select_none").click( function(){
		jQuery(':checkbox').prop("checked", false);
		return false;
	});
	jQuery('#rm-by-code').tablesorter();
	
	jQuery("#coloractivationform input").change( function(){
		var color = jQuery('#coloractivationform input:checkbox').attr('checked');
		jQuery.get('/django/salesorders/coloractivation', {
			"color": color
		}, function(data){
		});
	});
	
	$("#sales-order-by-lineitem th").click(function() {
		if ( $('#coloractivationform input:checkbox').attr('checked') ) {
			sortwithcolor_lineitem( $(this).parent().children().index( this ) + 1 );
		} else {
			sortplain($(this).parent().children().index( this ) + 1);
		}
	});


//	jQuery('#flavor-list tbody tr').hover(
//	  function () {
//	    $(this).attr('bgcolor', '#99CCFF');
//	  }, 
//	  function () {
//	    $(this).attr('bgcolor', '#FFFFFF');
//	  }
//	);
//	jQuery('#sales-order-by-lineitem tbody tr').hover(
//	  function () {
//	    $(this).attr('bgcolor', '#99CCFF');
//	  }, 
//	  function () {
//	    $(this).attr('bgcolor', '#FFFFFF');
//	  }
//	);
//	
//	jQuery('#sales-order-list tbody tr').hover(
//	  function () {
//	    $(this).attr('bgcolor', '#99CCFF');
//	  }, 
//	  function () {
//	    $(this).attr('bgcolor', '#FFFFFF');
//	  }
//	);
	
	jQuery('#add-formula-row-button').click(function(){
		var form_id = $('#id_form-TOTAL_FORMS').val();
		jQuery('#id_form-TOTAL_FORMS').val(Number(form_id)+1);
		
		jQuery('#formula-rows tr:last').after(
			'<tr class="formula_row">' + 
			'<td class="number-cell"><input type="text" name="form-' + form_id + '-ingredient_number" id="id_form-' + form_id + '-ingredient_number" /></td>' +
			'<td class="amount-cell"><input type="text" name="form-' + form_id + '-amount" id="id_form-' + form_id + '-amount" /></td>' +
			'<td class="name-cell"></td>' +
			'<td class="cost-cell"></td>' +
			'<td class="ingredient_pk-cell" style="display:none"> <input> </td>' +
			'<td class="del-row"><input type="button" value="X" onclick="delete_row(this.parentNode.parentNode.rowIndex)"></td>' +
			'</tr>');
		jQuery('#id_form-' + form_id + '-ingredient_number').focus();
		return false;
	});
	
	jQuery('#add-poli-row-button').click(function(){
		var form_id = $('#purchaseorderlineitem_set-TOTAL_FORMS').val();
		jQuery('#id_form-TOTAL_FORMS').val(Number(form_id)+1);
		
		jQuery('#poli-rows tr:last').after(
			'<tr>' + 
			'<td class="pin-cell">' +
				'<input id="id_purchaseorderlineitem_set-' + form_id + '-raw_material" type="hidden" name="purchaseorderlineitem_set-' + form_id + '-raw_material" value="" size="40" />' +
				'<input type="hidden" name="purchaseorderlineitem_set-' + form_id + '-id" value="" id="id_purchaseorderlineitem_set-' + form_id + '-id" />' +
				
				'<input id="id_form-' + form_id + '-ingredient_number" type="text" name="form-' + form_id + '-ingredient_number" value="" size="40" />' +
				
			'</td>' +
			'<td class="quantity-cell"><input type="text" name="form-' + form_id + '-quantity" id="id_form-' + form_id + '-quantity" /></td>' +
			'<td class="package_size-cell"><input type="text" name="form-' + form_id + '-package_size" id="id_form-' + form_id + '-package_size" /></td>' +
			'<td class="price-cell"></td>' +
			'<td class="name-cell"></td>' +
			'<td class="del-row"><input type="button" value="X" onclick="delete_row(this.parentNode.parentNode.rowIndex)"></td>' +
			'</tr>');
		jQuery('#id_form-' + form_id + '-ingredient_number').focus();
		return false;
	});
	
	
	jQuery('#add-retain-row-button').click(function(){
		var form_id = $('#id_form-TOTAL_FORMS').val();
		jQuery('#id_form-TOTAL_FORMS').val(Number(form_id)+1);
		
		jQuery('#retain-rows tr:last').after(
			'<tr>' + 
			'<td class="number-cell"><input type="text" name="form-' + form_id + '-flavor_number" id="id_form-' + form_id + '-flavor_number" /></td>' +
			'<td class="lot-cell"><input type="text" name="form-' + form_id + '-lot_number" id="id_form-' + form_id + '-lot_number" /></td>' +
			'<td class="name-cell"></td>' +
			'<td class="del-row"><input type="button" value="X" onclick="delete_row(this.parentNode.parentNode.rowIndex)"></td>' +
			'</tr>');
		jQuery('#id_form-' + form_id + '-ingredient_number').focus();
		return false;
	});
	
	jQuery('#formulaedit-filterselect input:checkbox').change( function() {
		filter_update();
	});
	
	jQuery('#formula-rows').delegate('input', 'keyup', function (e) {
		var $this = $(this);
		var row = $this.closest("tr");
		update_formula_row(row);
	});
	
	jQuery('#poli-rows').delegate('input', 'keyup', function (e) {
		var $this = $(this);
		var row = $this.closest("tr");
		update_poli_row(row);
	});
	
	jQuery('#matchform').delegate('input[name=percentage]', 'keyup', function (e) {
		clearTimeout(t);
		t = setTimeout("update_solution_percentage()", 750);
	});
	
	jQuery('#poli-rows').delegate('.pin-cell input', 'keyup', function(e) {
		var $this = $(this);
		var row = $this.closest("tr");
		$this.autocomplete({
			source: '/django/access/ingredient_autocomplete',
			minLength: 1,
			select: function( event, ui ) {
				// ui.item.value is the item of interest
				row.find(".pin-cell input[id$='raw_material']").val( ui.item.value );
				update_poli_row(row);
			}
		});
	});
	
	if(jQuery("#formula-rows").length > 0) {
		jQuery(document).ready(function() {
			console.log("The page has just been refreshed");
			jQuery('input:checkbox').removeAttr('checked');
			filter_rows();
			t = setTimeout(console.log(jQuery('.filter_message').length),2000);
			if(jQuery('.filter_message').length == 0) {
				jQuery('#formula-submit-button').show();
			} else {
				jQuery('#formula-submit-button').hide();
			}
		});
	}
	
	jQuery('#formula-rows').delegate('.number-cell input', 'keyup', function(e) {
		var $this = $(this);
		var row = $this.closest("tr");
		//update_formula_row(row);
		$this.autocomplete({
			source: '/django/access/ingredient_autocomplete',
			minLength: 1,
			select: function( event, ui ) {
				// ui.item.value is the item of interest
				row.find('.number-cell input').val( ui.item.value )
				update_formula_row(row);
			}
		});
	});
	
	function update_poli_row (row) {
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

	

	jQuery("#matchform select[name=solvent]").delegate('', 'change', function (e) {
		var $this = $(this)[0];
		if ($this.value == '') {
			return;
		}
		jQuery.post('/django/solutionfixer/process_solvent_update',
			{
				solution_id: jQuery('#solution_id').html(),
				solvent_id: $this.value
			},
			function (data) {
				return;
		}, 'json');
	
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
