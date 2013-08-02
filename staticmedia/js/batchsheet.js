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
}


var refresh_batchsheet = function(e) {
	delay(function() {
			jQuery.get('/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
				{batch_amount: jQuery('#id_batch_amount').val(),
				lot_number: jQuery('#id_lot_number').val()},
				put_batchsheet_data, 'json');
			return false;
		}, 100);
}

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
}

var populate_form_from_string = function() {
  jQuery('#id_flavor_number').val( getParameterByName('flavor_number') );
  jQuery('#id_batch_amount').val( getParameterByName('batch_amount') ); 
  refresh_batchsheet();
}

jQuery(document).ready(function(){	
	
       populate_form_from_string();
	
	$('#id_flavor_number').keyup( refresh_batchsheet );
	$('#id_batch_amount').keyup( refresh_batchsheet );
	$('#id_lot_number').keyup( refresh_batchsheet );
	
	$('#print_link').click(function(e) {
		var batch_amount = jQuery('#id_batch_amount').val();
		if (batch_amount == 0) {
			alert("Batch amount should not be zero.");
			return false;
		}
		$('input').attr('readonly', 'readonly');
		jQuery.get('/django/batchsheet/lot_init/',
			{
				flavor_number:jQuery('#id_flavor_number').val(),
				amount: batch_amount,
				lot_number: jQuery('#id_lot_number').val()
			},
			function(data) {
				var img_link='<img src=/django/batchseet/barcode/' + data.lot_number + ' align="top" />';
				jQuery('#titleright img').html(img_link);
				jQuery('#lot_number').html(data.lot_number);
				jQuery('#print_warning').hide();
				jQuery('#batchsheet').removeClass('do_not_print');
				//console.log("print");
				window.print();
                                //$('#print_link').remove();
		}, 'json');
	});
	
	$('#next_lot_link').click(function(e) {
		jQuery.get('/django/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
			{
				batch_amount: jQuery('#id_batch_amount').val(),
				get_next_lot: 1,
			},
			put_batchsheet_data, 'json');
	});
	
	$('#refresh_link').click(function(e) {
		window.location = "/django/batchsheet/"
	});
});
