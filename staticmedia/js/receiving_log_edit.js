function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+-)');
    var replacement = prefix + '-' + ndx + '-';
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.name) {
        el.name = el.name.replace(id_regex, replacement);
        //Change the value of the r_number within the row (can't just change it to the index)
        if (el.name.includes("r_number")) $(el).val(next_r_number + ndx - number_of_already_created_receiving_logs);
    }
}

function deleteForm(btn, prefix) {
    console.log('deleting form');
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());

    $(btn).parents('.receiving-log-row').remove();
    var forms = $('.new-receiving-log'); // Get all the forms
    // Update the total number of forms (1 less than before)
    $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
    var i = 0;

    var id_regex = new RegExp('Receiving Log ' + '\\d+');

    // Go through the forms and set their indices, names and IDs
    for (formCount = forms.length; i < formCount; i++) {

        //Replace receiving log headers to display correct index - 'Receiving Log 2'
        replacement_header = "Receiving Log " + (i + 1 + number_of_already_created_receiving_logs);
        panel_heading = $(forms.get(i)).find(".panel-heading");

        new_heading = panel_heading.html().replace(id_regex, replacement_header);
        panel_heading.html(new_heading);

        //Go through all input and select boxes and update the form indices
        $(forms.get(i)).find("input, select, label").each(function () {
            updateElementIndex(this, prefix, i + number_of_already_created_receiving_logs);
        });

    }

    return false;
}

function addForm(btn, prefix) {

    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    // Clone a form (without event handlers) from the first form
    var row = $(".receiving-log-row:first").clone(false).get(0);
    // Insert it after the last form
    $(row).removeAttr('id').hide().insertAfter(".receiving-log-row:last").slideDown(300);

    // Remove the bits we don't want in the new row/form
    // e.g. error messages
    $(".errorlist", row).remove();
    $(row).children().removeClass("error");

    // Relabel or rename all the relevant bits
    $(row).switchClass('already-created','new-receiving-log');
    $(row).find("table").find("input, select, label").each(function () {
        updateElementIndex(this, prefix, formCount);
        if (($(this).prop("tagName") != 'SELECT') && (this.type != "hidden")) {
            $(this).val("");
        }
        if (this.type == "hidden") {
            $(this).val("False");
        }
    });

    // Add an event handler for the delete item/form link
    $(row).find(".delete").click(function () {
        return deleteForm(this, prefix);
    });

    // Update the Receiving Log # in the panel header, and add a delete button to new rows
    $(row).find(".panel-heading").text("Receiving Log " + (formCount + 1)).append(
        "<button type='button' id='delete' class='btn btn-danger pull-right move-btn-up' aria-label='Left Align'> <span class='glyphicon glyphicon-trash vcenter' aria-hidden='true'> </span> </button>"
    );

    // Update the R Number field in the new row
    $(row).find(".r-number-field input").val(formCount + next_r_number - number_of_already_created_receiving_logs);

    // Update the total form count
    $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);

}

function get_next_r_number() {
    jQuery.get('/qc/get_next_r_number',
        {},
        function(data){
            window.next_r_number = data.next_r_number;
        },
        'json'
    );
    console.log('getting r number');
}

function update_total_amount_received() {
    var total = 0;

    //Iterate through each amount-received-field and add its value to the total (unless it's an empty string)
    $('.amount-received-field input').each(function() {
        if ($(this).val() === "") {
            total += 0;
        }
        else {
            total += parseFloat($(this).val());
        }
    });

    window.total_amount_received = total;

    $('.total-amount-received-value').text(total);

    if (total < total_amount_requested) {
        $('.total-tracker').switchClass("alert-success","alert-warning");
    }
    else {
        $('.total-tracker').switchClass("alert-warning","alert-success");
    }
}

function update_r_numbers() {
    // This takes some code from the delete_row function, it just iterates through the rows and updates the r_numbers
    // It also updates all the form indices but that's not really needed

    get_next_r_number();

    // Here we select the receiving logs which have not been created yet
    var forms = $('.new-receiving-log');
    var i = 0;
    // Go through the forms and update their r numbers
    for (formCount = forms.length; i < formCount; i++) {

        current_row = forms.get(i);
        $(current_row).find(".r-number-field input").val(i + next_r_number);

    }


}

function validate_submit(button) {
    //This function is run from the html onsubmit event.
    //It figures out which submit button was pressed and alerts the user if they are either trying to:
    // a. Close the receiving log if the requested amount hasn't been reached
    // b. Leave the receiving log open when teh requested amount has already been reached

    if (button.name === 'submit-close') {
        if (total_amount_received < total_amount_requested) {
            return confirm('Only received ' + total_amount_received + ' out of ' + total_amount_requested
                + ' lbs. Do you still want to close this receiving log?');
        }
    }
    else if (button.name === 'submit-open') {
        if (total_amount_received >= total_amount_requested) {
            return confirm('Already received more than the requested amount.  Are you sure you want to keep this receiving log open?');
        }
    }
}

jQuery(document).ready(function() {

    window.number_of_already_created_receiving_logs = $('.already-created').length;

    // Attach the total_amount_requested variable to the window objects so it can be accessed from any function
    window.total_amount_requested = parseInt($('.total-amount-requested-value').text());
    update_total_amount_received();

    // Set the next_r_number variable to the correct number (based on how many rm retains were created this year)
    get_next_r_number();

    //Update the 'next_r_number' variable every minute in case new retains are created while the form is being filled out
    setInterval(update_r_numbers, 60000);

    // The following line resets the TOTAL_FORMS management form value to its intended initial value.
    // Without doing this, the TOTAL_FORMS value would persist through page refreshes
    $("#id_form-TOTAL_FORMS").val($(".receiving-log-row").length);

    // Register the click event handlers
    $("#add-receiving-log").click(function () {
        return addForm(this, "form");
    });

    $(document).on('click', '#delete', function () {
        return deleteForm(this, "form");
    });

    //The selector here needs to contain any dynamically created fields (the new rows)
    // in order for the event handler to work on them
    $('#receiving-log-dynamic-fields').on('keyup','.amount-received-field', function() {
        update_total_amount_received();
    });

    //If the poli is closed, allow the user to reopen and edit fields by checking a box
    //Check if the toggle-fields selector exists
    if ($('#toggle-fields').length) {
        var checked = $('#toggle-fields').is(':checked');
        $('#receiving-log-static-fields, #receiving-log-dynamic-fields, #form-buttons').find('input, select').prop('disabled', !checked);

        $('#receiving-log-closed').on('click', '#toggle-fields', function() {
            checked = $('#toggle-fields').is(':checked');
            $('#receiving-log-static-fields, #receiving-log-dynamic-fields, #form-buttons').find('input, select').prop('disabled', !checked);
            if (checked) {
                $('#receiving-log-closed').switchClass('alert-danger','alert-success');
            }
            else {
                $('#receiving-log-closed').switchClass('alert-warning','alert-success');
            }

        })
    }

});
