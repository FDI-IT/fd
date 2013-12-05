// this variable designates a timeout to recalculate the total cost
var t;




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
	
	jQuery('#pagination-bar a#show_all_revisions').click(function() {
	    if (window.confirm('Showing all objects may take some time to load.  Would you like to continue?')) {
    		var url = $(this).attr('href');
    		$('#content').load(url);
	    }
	    else {
	    	return false;
	    }
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

/*
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
		return false;
	});	
*/

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
	var menu = jQuery('#edit_menu');
	menu.menu();
	jQuery('#experimental_edit_link').click(function(event) {
		jQuery('#edit_menu').show().position({
			my:'left top',
			at:'left bottom',
			of:event,
		});
		jQuery(document).one("click", function() {
			menu.hide();
		});
		return false;
	});



});
