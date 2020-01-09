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

var ajax_refresh_batchsheet = function(e) {
	return jQuery.get('/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
		{
			batch_amount: jQuery('#id_batch_amount').val(),
			packaging_requirements: jQuery('#id_packaging_requirements').val()
		},
		put_batchsheet_data, 'json'
	);
};

var refresh_batchsheet = function(e) {
	ajax_refresh_batchsheet(e).done(activate_print_links);
	return false;
};

var delay_refresh_batchsheet = function(e) {
	deactivate_print_links();
	delay(refresh_batchsheet, 150);
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
};

var image_safe_print = function() {
	jQuery('input').attr('readonly', 'readonly');
	jQuery('#print_warning').hide();
	jQuery('#batchsheet').removeClass('do_not_print');
	jQuery('#batchsheet').waitForImages( function() {
		window.print();
	});
};

var print_with_next_lot_number = function(data) {

  jQuery.ajax({
    async:false,
    type: 'GET',
    contentType:'json',
    url:'/batchsheet/get_last_lot/',
    // datatype:'json'
    data:{
      flavor_number:jQuery('#id_flavor_number').val(),
    },

    success: function(resp){
      if(resp.threeyears){
        if(confirm('This product has not been sold in over 3 years - do you still want to create this lot?')){
          put_batchsheet_data(data);
          jQuery.ajax({
              async: false,
              type: 'GET',
              contentType: 'json',
              url: '/batchsheet/lot_init/',
              data:
              {
                flavor_number:jQuery('#id_flavor_number').val(),
                amount: jQuery('#id_batch_amount').val(),
                //update_inventory: jQuery('#id_update_rm_inventory').is(':checked')
              },
              success: function(data) {
                image_safe_print();
              },
              error: function(data) {
                alert('Unable to initialize lot number. The lot number is NOT RECORDED in the system. Please try again. Message: ' + data);
              }
            });
        }
      }
      else{
        put_batchsheet_data(data);
        jQuery.ajax({
            async: false,
            type: 'GET',
            contentType: 'json',
            url: '/batchsheet/lot_init/',
            data:
            {
              flavor_number:jQuery('#id_flavor_number').val(),
              amount: jQuery('#id_batch_amount').val(),
              //update_inventory: jQuery('#id_update_rm_inventory').is(':checked')
            },
            success: function(data) {
              image_safe_print();
            },
            error: function(data) {
              alert('Unable to initialize lot number. The lot number is NOT RECORDED in the system. Please try again. Message: ' + data);
            }
          });
      }
    },


  });

  // jQuery.ajax({
  // 		async: false,
  // 		type: 'GET',
  // 		contentType: 'json',
  // 		url: '/batchsheet/lot_init/',
  // 		data:
  // 		{
  // 			flavor_number:jQuery('#id_flavor_number').val(),
  // 			amount: jQuery('#id_batch_amount').val(),
  // 			//update_inventory: jQuery('#id_update_rm_inventory').is(':checked')
  // 		},
  // 		success: function(data) {
  //
  // 			image_safe_print();
  // 		},
  // 		error: function(data) {
  // 			alert('Unable to initialize lot number. The lot number is NOT RECORDED in the system. Please try again. Message: ' + data);
  // 		}
  // 	});
};

var print_with_no_lot_number = function() {
	image_safe_print();
};

var ajax_get_batchsheet_with_next_lot = function() {

  	jQuery.get('/batchsheet/batchsheet_print/' + jQuery('#id_flavor_number').val() + '/',
  		{
  			batch_amount: jQuery('#id_batch_amount').val(),
  			packaging_requirements: jQuery('#id_packaging_requirements').val(),
  			get_next_lot: 1,
  		},
  		print_with_next_lot_number, 'json'
  	);
};

var print_click_handler = function(e) {
	if(!jQuery("#batchsheet").hasClass('do_not_print')) {
		// this means the batchsheet has already been printed
		// and image_safe_print was already called
		if(confirm("Would you like to re-print this batch sheet as-is?")) {
			window.print();
			return false;
		} else {
			return false;
		}
	}

	if (! check_flavor_number() ) {
		return false;
	}

	if (! check_batch_amount() ) {
		return false;
	}

	print_with_no_lot_number();
};

var next_lot_click_handler = function(e) {
	if(!jQuery("#batchsheet").hasClass('do_not_print')) {
		// this means the batchsheet has already been printed
		// and image_safe_print was already called
		if (jQuery('#lot_number').length==0) {
			if(confirm("Would you like to add a lot number and re-print?")) {
				ajax_get_batchsheet_with_next_lot();
				return false;
			} else {
				return false;
			}
		} else {
			if(confirm("Would you like to re-print this batch sheet as-is?")) {
				window.print();
				return false;
			} else {
				return false;
			}
		}
	}

	if (! check_flavor_number() ) {
		return false;
	}

	if (! check_batch_amount() ) {
		return false;
	}

	ajax_get_batchsheet_with_next_lot();
};

var check_flavor_number = function() {
	if (jQuery('#id_flavor_number').val() > 0) {
		return true;
	} else {
		alert("Enter a valid flavor number.");
		return false;
	}
};

var check_batch_amount = function() {
	if (jQuery('#id_batch_amount').val() > 0) {
		return true;
	} else {
		alert("Enter a valid batch amount.");
		return false;
	}
};

var initial_link_alert = function() {
	alert("Please get a valid batchseet before printing.");
};

var deactivated_link_handler = function(e) {
	alert('The batchsheet needs more time to load. Please close this alert and wait a moment.');
	if(e.currentTarget.attributes.id.textContent == 'print_link') {
		var done_function = print_click_handler;
	} else {
		var done_function = next_lot_click_handler;
	}
	// the reason to use delay is to clear any existing timers that may
	// interfere with the refresh that we want to do here.
	// we ran into some behavior where if the next lot print link was
	// clicked while waiting, then this refresh collides with the delayed
	// refresh that's still firing from the last keyup event.
	delay(function() {
		ajax_refresh_batchsheet().done(done_function);
	}, 10);
	return false;
};

var activate_print_links = function() {
	$('#print_link').unbind('click').click( print_click_handler );
	$('#next_lot_link').unbind('click').click( next_lot_click_handler );
};

var deactivate_print_links = function(e) {
	$('#print_link, #next_lot_link').unbind('click').click( deactivated_link_handler );
};

var populate_form_from_qstring = function() {
	jQuery('#id_flavor_number').val( getParameterByName('flavor_number') );
	jQuery('#id_batch_amount').val( getParameterByName('batch_amount') );
	refresh_batchsheet();
};

jQuery(document).ready(function(){
	populate_form_from_qstring();

	$('#id_flavor_number, #id_batch_amount, #id_packaging_requirements').keyup( delay_refresh_batchsheet );
	$('#id_flavor_number, #id_batch_amount, #id_packaging_requirements').keydown( deactivate_print_links );

	$('#print_link, #next_lot_link').click( initial_link_alert );

	$('#refresh_link').click(function(e) {
		window.location = "/batchsheet/"
	});
});
