var BATCHSHEET = {};

var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();



var getParameterByName = function (name) {
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
  var regexS = "[\\?&]" + name + "=([^&#]*)";
  var regex = new RegExp(regexS);
  var results = regex.exec(window.location.search);
  if(results == null)
    return "";
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
};


var refresh_batchsheet = function(e) {
	delay(function() {
			jQuery.get('/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
				{batch_amount: jQuery('#id_batch_amount').val(),
				lot_number: jQuery('#id_lot_number').val()},
				put_batchsheet_data, 'json');
			return false;
		}, 400);
	console.log("WOW");
};

var refresh_before_print = function(e) {
	// delay(function() {
		// console.log("WTF");
			// jQuery.get('/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
				// {batch_amount: jQuery('#id_batch_amount').val(),
				// lot_number: jQuery('#id_lot_number').val()},
				// put_batchsheet_data, 'json');
			// return false;
		// }, 0);
		
		jQuery.ajax({
			async: false,
			type: 'GET',
			contentType: 'json',
			url: '/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
			data: 
			{
					batch_amount: jQuery('#id_batch_amount').val(),
					lot_number: jQuery('#id_lot_number').val()
			},
			success: function(data) {
				console.log("WTF");
			}
		});
};

var put_batchsheet_data = function(data) {
	$('#bubble_container').html(data.sidebar);
	jQuery('#batchsheet').html(data.batchsheet);
	
	$('#formula').tablesorter({
		headers: {
			0: {sorter: 'digit'},
			1: {sorter: 'text'},
			2: {sorter: 'text'},
			3: {sorter: 'digit'},
			4: {sorter: 'digit'},
		}
	});		
	$('#id_lot_number').val(data.lot_number);
};

var populate_form_from_string = function() {
  jQuery('#id_flavor_number').val( getParameterByName('flavor_number') );
  jQuery('#id_batch_amount').val( getParameterByName('batch_amount') ); 
  refresh_batchsheet();
};

var print_batchsheet = function(update) {
	refresh_before_print();
	update = typeof update !== 'undefined' ? update : 'false';
	$('input').attr('readonly', 'readonly');
	
	jQuery.ajax({
		async: false,
		type: 'GET',
		contentType: 'json',
		url: '/django/batchsheet/lot_init/',
		data: 
		{
			flavor_number:jQuery('#id_flavor_number').val(),
			amount: jQuery('#id_batch_amount').val(),
			lot_number: jQuery('#id_lot_number').val(),
			update: update
		},
		success: function(data) {
			var img_link='<img src=/django/batchsheet/barcode/' + data.lot_number + ' align="top" />';
			console.log('request some come after this console log');
			jQuery('#titleright img').html(img_link);
			jQuery('#lot_number').html(data.lot_number);
			// jQuery.get('/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
			// {
				// batch_amount: jQuery('#id_batch_amount').val(),
			// },
			// put_batchsheet_data, 'json');
			jQuery('#print_warning').hide();
			jQuery('#batchsheet').removeClass('do_not_print');
			//console.log("print");

			//TODO wait for img_link

			// jQuery('#titleright img').load( function() {
				// window.print();
			// });

                            //$('#print_link').remove();
		}	
	});
	
	
	// jQuery.get('/django/batchsheet/lot_init/',
		// {
			// flavor_number:jQuery('#id_flavor_number').val(),
			// amount: jQuery('#id_batch_amount').val(),
			// lot_number: jQuery('#id_lot_number').val(),
			// update: update
		// },
		// function(data) {
			// var img_link='<img src=/django/batchseet/barcode/' + data.lot_number + ' align="top" />';
			// jQuery('#titleright img').html(img_link);
			// jQuery('#lot_number').html(data.lot_number);
			// // jQuery.get('/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
			// // {
				// // batch_amount: jQuery('#id_batch_amount').val(),
			// // },
			// // put_batchsheet_data, 'json');
			// jQuery('#print_warning').hide();
			// jQuery('#batchsheet').removeClass('do_not_print');
			// //console.log("print");
// 
                            // //$('#print_link').remove();
		// }, 'json');	
	
	// jQuery(document).ready(function() {
		// window.print();
	// });

		
	// jQuery(window).load(function() {
		// window.print();
	// });
	
	// jQuery('#titleright img').load( function() {
		// window.print();
	// });
	
	jQuery('#titleright img').ready( function() {
		window.print();
	});		
};

var dialog_cancel = function() {
	jQuery(this).dialog("close");
};
var dialog_update = function() {
	jQuery(this).dialog("close");
	print_batchsheet('true');
};
var dialog_create = function() {
	jQuery('#id_lot_number').val(BATCHSHEET.next_lot_number);
	refresh_batchsheet();
	jQuery(this).dialog("close");
	print_batchsheet();
};

var dialog_reprint = function() {
	jQuery(this).dialog("close");
	print_batchsheet();
};


jQuery(document).ready(function(){	
	$("#update_dialog").dialog({
		resizable: false,
		width: 850,
		height: 210,
		modal: true,
		autoOpen: false,
		buttons: {
			"Cancel":dialog_cancel,
			"Update Lot with New Weight": dialog_update,
			"Create New Lot with Next Number": dialog_create,
		}		
	});
	
	$("#create_dialog").dialog({
		resizable: false,
		width: 550,
		height: 210,
		modal: true,
		autoOpen: false,
		buttons: {
			"Cancel": dialog_cancel,
			"Create New Lot with Next Lot Number": dialog_create,
		}		
	});
	
	$("#next_lot_dialog").dialog({
		resizable: false,
		width: 550,
		height: 190,
		modal: true,
		autoOpen: false,
		buttons: {
			"Cancel": dialog_cancel,
			"Use Next Lot Number": dialog_create,
		}		
	});	
	
	$("#print_existing_dialog").dialog({
		resizable: false,
		width: 700,
		height: 210,
		modal: true,
		autoOpen: false,
		buttons: {
			"Cancel": dialog_cancel,
			"Use Next Lot Number": dialog_create,
			"Re-Print Batchsheet": dialog_reprint,
		}		
	});		
	
       populate_form_from_string();
	
	$('#id_flavor_number').keyup( refresh_batchsheet );
	$('#id_batch_amount').keyup( refresh_batchsheet );
	$('#id_lot_number').keyup( refresh_batchsheet );
	
	$('#print_link').click(function(e) {
		//jQuery("#update_dialog").dialog("option", "title", "JFLAKSDJLAKSDJ").dialog("open");
		
		var batch_amount = jQuery('#id_batch_amount').val();
		if (batch_amount == 0) {
			alert("Batch amount should not be zero.");
		}
		else if(!jQuery("#batchsheet").hasClass('do_not_print')) {
			if(confirm("Would you like to re-print this batch sheet?")) {
				print_batchsheet();
			}
		}
		else {
			jQuery.ajax({
			     async: false,
			     type: 'GET',
			     url: '/django/batchsheet/check_lot_number/',
			     data: 
			     	{
			     		lot_number:jQuery('#id_lot_number').val()
			     	},
			     success: function(data) {
			     	BATCHSHEET.next_lot_number = data.next_lot_number;
			        
			        console.log("next lot number: " + BATCHSHEET.next_lot_number);
					if (data.used == 'true') {
						// console.log(data.flavor_number);
						// console.log(data.flavor_number == jQuery("#id_flavor_number").val());
						if (data.flavor_number == jQuery("#id_flavor_number").val()) {
							if (Number(data.amount) == Number(jQuery("#id_batch_amount").val())) { //if same flavor number AND amount
								var title = "This exact lot already exists.";
								jQuery("#print_existing_dialog").html("<b>Lot Number:</b> " + jQuery('#id_lot_number').val() + "<br\><b>Existent Flavor Number:</b> " + data.flavor_number + "<br\><b>Existent Amount:</b> " + data.amount);
								jQuery("#print_existing_dialog").dialog("option","title",title).dialog("open").css("text-align","center");
							}
							else {
								var title = "This lot number already exists with the same flavor number, but different weight.";
								jQuery("#update_dialog").html("<b>Lot Number:</b> " + jQuery('#id_lot_number').val() + "<br\><b>Flavor Number:</b> " + data.flavor_number + "<br\><b>Old weight:</b> " + data.amount + " <b>New weight:</b> " + jQuery("#id_batch_amount").val());
								jQuery("#update_dialog").dialog("option","title",title).dialog("open").css("text-align","center");
							}
						}
						
						else {
							var title = "This lot number already exists with a different flavor.";
							jQuery("#create_dialog").html("<b>Lot Number:</b> " + jQuery('#id_lot_number').val() + "<br\><b>Existent Flavor Number:</b> " + data.flavor_number + "<br\><b>Existent Amount:</b> " + data.amount);
							jQuery("#create_dialog").dialog("option","title",title).dialog("open").css("text-align","center");
						}
					}
					else {
						if (data.use_next_lot == 1) {
							var title = "No lot number was entered.  Would you like to use the next one?";
							jQuery("#next_lot_dialog").html("<b>Next Lot Number:</b> " + data.next_lot_number);
							jQuery("#next_lot_dialog").dialog("option","title",title).dialog("open").css("text-align","center");							
						}
						// jQuery('#id_lot_number').attr("value", data.lot_number);
						else {
							print_batchsheet();
						}
					}
			     }
			     
			});
		}
	});
	
	$('#next_lot_link').click(function(e) {
		jQuery.get('/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
			{
				batch_amount: jQuery('#id_batch_amount').val(),
				get_next_lot: 1,
			},
			put_batchsheet_data, 'json');
		//refresh_batchsheet();
	});
	
	$('#refresh_link').click(function(e) {
		window.location = "/django/batchsheet/"
	});
});
