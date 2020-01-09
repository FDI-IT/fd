var EXPERIMENTAL_LABEL_EDIT = {};
EXPERIMENTAL_LABEL_EDIT.checked_boxes = [];

EXPERIMENTAL_LABEL_EDIT.update_product_label_name = function() {
    clearTimeout(EXPERIMENTAL_LABEL_EDIT.t);
    var my_val = jQuery('[name$="product_name"]').val().trim();
    if (my_val == "") {
        jQuery('#product-label-name')
            .addClass('no-user-data-yet')
            .html('[Name]');
    } else {
        jQuery('#product-label-name')
            .removeClass('no-user-data-yet')
            .html(my_val);
    }
};

EXPERIMENTAL_LABEL_EDIT.update_natart = function() {
    var my_val = jQuery('[name$="natart"]').val();
    if (my_val == "" ) {
        jQuery('#product-label-natart')
            .addClass('no-user-data-yet')
            .html('[NatArt]');
            return;

    } else {
        jQuery('#product-label-natart')
            .removeClass('no-user-data-yet')
            .html(my_val);
        if (my_val == "Nat") {
            EXPERIMENTAL_LABEL_EDIT.enable_natural_options();
        } else {
            EXPERIMENTAL_LABEL_EDIT.disable_natural_options();
        }
    }
};

EXPERIMENTAL_LABEL_EDIT.natural_category_selector = '[name$="wonf"], [name$="natural_type"], [name$="organic_compliant_required"], [name$="organic_certified_required"]';

EXPERIMENTAL_LABEL_EDIT.disable_natural_options = function() {
    jQuery(EXPERIMENTAL_LABEL_EDIT.natural_category_selector).each(function() {
        var $this = $(this);
        $this.attr("disabled",true).closest('p').addClass('temporarily-disabled');
        $this.prop("checked", false);
    });
};

EXPERIMENTAL_LABEL_EDIT.enable_natural_options = function() {
    jQuery(EXPERIMENTAL_LABEL_EDIT.natural_category_selector).each(function() {
        var $this = $(this);
        $this.attr("disabled",false).closest('p').removeClass('temporarily-disabled');
    });
};

EXPERIMENTAL_LABEL_EDIT.category_name_map = {
	'wonf':0,
	'natural_type':1,
	'organic_compliant_required':2,
	'organic_certified_required':9,
	'liquid':3,
	'dry':4,
	'spraydried':5,
	'concentrate':6,
	'oilsoluble':7,
	'flavorcoat':8,

};

EXPERIMENTAL_LABEL_EDIT.category_human_map = {
    0:'WONF',
    1:'Type',
    2:'OCOMP',
    9:'OCOMP',
    3:'',
    4:'Powdered',
    5:'Spray Dried',
    6:'Concentrate',
    7:'OS',
    8:'Flavorcoat®',
};

EXPERIMENTAL_LABEL_EDIT.incompatible_categories = [
    [0,1,"Can't be WONF and Type."],
    [3,4,"Can't be liquid and dry."],
    [3,5,"Can't be liquid and spray dried"],
    [4,5,"Can't be dry and spray dried."],
    [5,7,"Can't be spray dried and oil soluble."],
    [3,8,"Can't be flavorcoat and liquid."],
    [4,8,"Can't be flavorcoat and powdered."],
    [5,8,"Can't be flavorcoat and spray dried."],
    [6,8,"Can't be flavorcoat and concentrate."],
    [7,8,"Can't be flavorcoat and oil soluble."],
    [2,9,"Can't be organic compliant and organic certified."],
];

EXPERIMENTAL_LABEL_EDIT.check_tail_indices = function(token_indices, label_tokens) {
    for (var token_index in token_indices) {
        var my_token = token_indices[token_index];
        if ($.inArray(my_token, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1) {
            label_tokens.push(EXPERIMENTAL_LABEL_EDIT.category_human_map[my_token]);
        }
    }
};

EXPERIMENTAL_LABEL_EDIT.build_label_tail = function() {
    var product_category = jQuery('#id_0-product_category option:selected').text();
    if (EXPERIMENTAL_LABEL_EDIT.checked_boxes.length == 0) {
        return [];
    }

    var label_tokens = [];
    var token_indices = [4,5,7,1];

    EXPERIMENTAL_LABEL_EDIT.check_tail_indices(token_indices, label_tokens);

    if ($.inArray(8, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1) {
        label_tokens.push(EXPERIMENTAL_LABEL_EDIT.category_human_map[8]);
    } else {
        label_tokens.push(product_category);
    }

    token_indices = [6,0,2,9];

    EXPERIMENTAL_LABEL_EDIT.check_tail_indices(token_indices, label_tokens);

    return label_tokens;
};


EXPERIMENTAL_LABEL_EDIT.check_label_tail = function() {
    var label_tokens = EXPERIMENTAL_LABEL_EDIT.build_label_tail();
    if (label_tokens.length > 0) {
        var label_tail = label_tokens.join(" ");
        jQuery('#product-label-category').removeClass('no-user-data-yet')
            .html(label_tail);
        jQuery('[name$="label_type"]').val(label_tail);
    } else {
        jQuery('#product-label-category').addClass('no-user-data-yet')
            .html('[Category]');
        jQuery('[name$="label_type"]').val("");
    }
};

EXPERIMENTAL_LABEL_EDIT.get_checked_boxes = function() {
    EXPERIMENTAL_LABEL_EDIT.checked_boxes = [];
    jQuery('input:checkbox:checked').each( function() {
        if (this.name.indexOf('0-') == 0) {
            var my_name = this.name.substring(2);
        } else {
            var my_name = this.name;
        }
        var my_enum = EXPERIMENTAL_LABEL_EDIT.category_name_map[my_name];
        EXPERIMENTAL_LABEL_EDIT.checked_boxes.push(my_enum);
    });
};

jQuery(document).ready(function(){

    if (jQuery('[name$="natart"]').val() != "Nat") {
        EXPERIMENTAL_LABEL_EDIT.disable_natural_options();
    }
    EXPERIMENTAL_LABEL_EDIT.update_natart();
    EXPERIMENTAL_LABEL_EDIT.update_product_label_name();
    EXPERIMENTAL_LABEL_EDIT.get_checked_boxes();
    EXPERIMENTAL_LABEL_EDIT.check_label_tail();

    jQuery('#content-left-half form').submit( function(event) {
        if (jQuery('[name$="natart"]').val() == "") {
            event.preventDefault();
            alert("Must select a value from the Nat/Art drop down.");
            return;
        }

        if (jQuery('[name$="product_name"]').val() == "") {
            event.preventDefault();
            alert("Must enter a name.");
            return;
        }

        if (($.inArray(3, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1) ||
            ($.inArray(4, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1) ||
            ($.inArray(5, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1) ||
            ($.inArray(8, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1)) {

        } else {
            event.preventDefault();
            alert("Must select one of the following phyiscal properties: liquid, dry, spray dried or flavorcoat.");
            return;
        }

    });

    jQuery('[name$="product_name"]').on('change keypress paste textInput input', function() {
        EXPERIMENTAL_LABEL_EDIT.t = setTimeout('EXPERIMENTAL_LABEL_EDIT.update_product_label_name()',250);
    });

    jQuery('[name$="product_category"]').change(EXPERIMENTAL_LABEL_EDIT.check_label_tail);
    jQuery('[name$="natart"]').change(EXPERIMENTAL_LABEL_EDIT.update_natart);

    jQuery('input:checkbox').change(function() {
        EXPERIMENTAL_LABEL_EDIT.get_checked_boxes();
        for (var i=0; i < EXPERIMENTAL_LABEL_EDIT.incompatible_categories.length; i++) {
            var my_cat = EXPERIMENTAL_LABEL_EDIT.incompatible_categories[i];
            var first = my_cat[0];
            var second = my_cat[1];
            if ($.inArray(first, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1) {
                if ($.inArray(second, EXPERIMENTAL_LABEL_EDIT.checked_boxes) != -1) {
                    alert(my_cat[2]);
                    $(this).prop("checked", false);
                    return;
                }
            }
        }
        EXPERIMENTAL_LABEL_EDIT.check_label_tail();
    });

});
