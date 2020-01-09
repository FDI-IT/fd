var dialog;

function changeFilter() {
    var filter_ids = [];
    var checked_boxes = $('.filter_checkbox:checked');

    checked_boxes.each(function() {
        filter_ids.push(this.value);
    });
    
    redirect_url = "/access/flavor_hazard_report/?filter_hazards=[" + filter_ids.join(",") + "]";
    window.location.replace(redirect_url);
}

function checkAll() {
  var cbs = document.getElementsByTagName('input');
  for(var i=0; i < cbs.length; i++) {
    if(cbs[i].type == 'checkbox') {
      cbs[i].checked = bx.checked;
    }
  }
}

jQuery(document).ready(function(){

    dialog = $("#dialog-form").dialog({
        autoOpen: false,
        height: 515,
        width: 540,
        modal: true,
        buttons: {
            "Change Filter": changeFilter,
            Cancel: function() {
                dialog.dialog( "close" );
            }
        },
        close: function() {
            dialog.dialog( "close" );
        }
    });

    jQuery("#change-filter").button().on("click", function() {
        dialog.dialog("open");
    });
    
});