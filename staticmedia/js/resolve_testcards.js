var lot_detail_submit = function(index, element) {
	var testcard_form_data = {};
	jQuery('div.testcard_form_container').each( function(o_index, testcard_form_container) {
		testcard_form_data[o_index] = {};
		jQuery( testcard_form_container ).find('input').each( function (i_index, element) {
			var $elem = jQuery(element);
			testcard_form_data[o_index][$elem.attr('name')] =  $elem.val();
		});
		var selected = jQuery( testcard_form_container ).find('option:selected');
		testcard_form_data[o_index][selected.parent().attr('name')] = selected.val();
		
	});
	testcard_form_data['product_info_form'] = {}
	jQuery('.product_info_form input').each( function (index, element) {
		var $elem = jQuery(element);
		testcard_form_data['product_info_form'][$elem.attr('name')] = $elem.val();
	});
	
	
	jQuery.post(window.location.pathname, JSON.stringify(testcard_form_data), function(data) {
		//
	});
}

var ajax_post = function() {
	var old_instance_pk = jQuery('div.current_loaded input[name="instance_pk"]').val();
	jQuery("div.current_loaded").fadeOut();
	var x = jQuery.post('/qc/resolve_testcards_ajax_post/', 
		jQuery('div.current_loaded form').serialize(),
		function (data) {
			jQuery("div.current_loaded").removeClass('current_loaded').fadeOut( function() {
				var sidebar_link = jQuery("div.ondeck").removeClass('ondeck').hide().fadeIn().addClass('current_loaded').data("sidebar_link");
				jQuery("#sidebar_links").append(sidebar_link);
				jQuery("div.testcard_form_container").append(data);	
                                jQuery(this).remove();
			});
			
			
	}, 'html');
};

$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

jQuery(document).ready(function() {
	jQuery(".testcard_form_container").delegate('.testcard_resolve_image', "click", function() {
			$('.hidden_image').removeClass('click_to_zoom');
			$(this).siblings('.hidden_image').addClass('click_to_zoom');
	});
	jQuery('.testcard_form_container').delegate('.hidden_image', "click", function() {
		$(this).removeClass('click_to_zoom');
	});

	jQuery('#lot_detail_submit').click( lot_detail_submit );
});
