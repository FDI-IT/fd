var PIN_CELL = 0;
var NA_CELL = 1;
var PREFIX_CELL =2
var NAME_CELL = 3;
var AMOUNT_CELL = 4;
var UNITCOST_CELL = 5;
var RELCOST_CELL = 6;
var LASTUPDATE_CELL = 7;

function popup_window(str_url) {
     var newwindow = window.open(str_url);
	 return newwindow;
};

function print_experimental_review(experimental_number) {
	var visible_data = jQuery('.tab_data:visible');
	if (visible_data.length == 0) {
		var copy_table = jQuery('#flat-table');
	} else {
		var copy_table = visible_data;
	}


	newwindow = popup_window('/access/experimental/' + experimental_number +'/print_review/');
	newwindow.onload = function (e) {
		var div_flavor_tabs = newwindow.document.getElementById('flavor-tabs');
		var new_table = copy_table.clone();
		var batch_weight = jQuery('#adjusted_weight').val();
		if (batch_weight == "") {
			batch_weight = 1000;
		}
		if ( new_table.is("table") ) {
			new_table.prepend('<caption>Batch Weight: '+ batch_weight +'</caption>').appendTo(jQuery(div_flavor_tabs));	
		} else {
			new_table.find('table').prepend('<caption>Batch Weight: '+ batch_weight +'</caption>')
			new_table.appendTo(jQuery(div_flavor_tabs));
		}
		newwindow.print();
	};
}

function print_review(flavor_number) {
	var visible_data = jQuery('.tab_data:visible');
	if (visible_data.length == 0) {
		var copy_table = jQuery('#flat-table');
	} else {
		var copy_table = visible_data;
	}
	newwindow = popup_window('/access/' + flavor_number +'/print_review/');
	newwindow.onload = function (e) {
		var div_flavor_tabs = newwindow.document.getElementById('flavor-tabs');
		var new_table = copy_table.clone();
		var batch_weight = jQuery('#adjusted_weight').val();
		if (batch_weight == "") {
			batch_weight = 1000;
		}
		if ( new_table.is("table") ) {
			new_table.prepend('<caption>Batch Weight: '+ batch_weight +'</caption>').appendTo(jQuery(div_flavor_tabs));	
		} else {
			new_table.find('table').prepend('<caption>Batch Weight: '+ batch_weight +'</caption>')
			new_table.appendTo(jQuery(div_flavor_tabs));
		}
		newwindow.print();
	};
}

function print_qc(flavor_number) {
	newwindow = popup_window('/qc/flavors/' + flavor_number +'/print/');
	newwindow.onload = function (e) {
		newwindow.print();		
	};
}

function spec_sheet(flavor_number) {
	newwindow = popup_window('/access/' + flavor_number +'/spec_sheet/');
	newwindow.onload = function (e) {
		newwindow.print();		
	};
}

// This will parse a delimited string into an array of
// arrays. The default delimiter is the comma, but this
// can be overriden in the second argument.
var LEGACY_AMOUNT_CELL = 7;
function consolidate() {
	if (document.getElementById('exploded') == null) {
		return;
	};

	// get a reference to the target div, remove any children from it,
	// and reset it.
  	consolidated_container = jQuery('#consolidated-table');
  	consolidated_container.empty();
  	consolidated_table = document.createElement("table");
  	consolidated_table.setAttribute("id", "consolidated");
  	consolidated_table.setAttribute("width", "100%");
  	var caption = document.createElement('caption');
  	caption.innerHTML = 'Consolidated Formula';
	consolidated_table.appendChild(caption);
  	consolidated_table.appendChild(document.getElementById('exploded').tHead.cloneNode(true));
  	consolidated_table_body = document.createElement("tbody");
	
	// this regex returns the class flavor-xx or raw_material-xx from a string of many classes
  	var id_regex = /(?:flavor|raw_material)\-[0-9]+/;
	
	// get a reference to the source data rows
	var trs = document.getElementById('exploded').rows;
	
	var consolidated_rows = {};
    // we start at var i = 1 to skip the header row 
  	jQuery('#exploded tr').each( function(index){
		if(index == 0) {
			return;
		}
		
		var tr = this;
	
		// if this row is invisible, ignore it
		if (tr.style.display == 'none') {
			return;
		}
		
		// if this row is a flavor expanded, ignore it
		if ($(tr).hasClass('flavor') &&
		$(tr).hasClass('expanded') &&
		$(tr).hasClass('parent')) {
			return;
		}
		
		var row_id = id_regex.exec(tr.className);
		
		if( consolidated_rows[row_id] ) {
			// old_val = Number(consolidated_table_body.childNodes[j].cells[AMOUNT_CELL].innerHTML);
			// this_val = Number(tr.cells[AMOUNT_CELL].innerHTML);
			// new_val = old_val + this_val;
			consolidated_rows[row_id] += Number(tr.cells[LEGACY_AMOUNT_CELL].innerHTML);
		} else {
			consolidated_rows[row_id] = Number(tr.cells[LEGACY_AMOUNT_CELL].innerHTML);
		}
	});
	
	var row_id;
	for (row_id in consolidated_rows) {
		var my_value = consolidated_rows[row_id];
		if (typeof my_value !== 'function') {
			var possible_clone_rows = jQuery('.' + row_id);
			var new_row;
			var i;
			for (i=0; i < possible_clone_rows.length; i+= 1) {
				if(possible_clone_rows[i].style.display == 'none') {
					continue;
				} else {
					new_row = possible_clone_rows[i].cloneNode(true);
					break;
				}
			}
			new_row.cells[LEGACY_AMOUNT_CELL].innerHTML = my_value.toFixed(3);
			var unitcost = new_row.cells[LEGACY_AMOUNT_CELL-1].innerHTML;
			var relativecost = Number(unitcost) / 1000 * my_value;
			new_row.cells[LEGACY_AMOUNT_CELL+1].innerHTML = relativecost.toFixed(3);
			consolidated_table_body.appendChild(new_row);
		}
	}
	
	consolidated_table.appendChild(consolidated_table_body);
   	consolidated_container.append(consolidated_table);
	$('#consolidated td:first-child').each( function () {
		$(this).attr('style', "")
	});
	
   	$("#consolidated").tablesorter({
		headers: {
			0: {
				sorter: 'text'
			},
			1: {
				sorter: 'link-digit'
			},
			2: {
				sorter: 'text'
			},
			3: {
				sorter: 'text'
			},
			4: {
				sorter: 'text'
			},
			5: {
				sorter: 'shortDate'
			},
			6: {
				sorter: 'digit'
			},
			7: {
				sorter: 'digit'
			},
			8: {
				sorter: 'digit'
			}
		}
	}); 
}

function flat_review_popup(flavor_number) {
	newwindow = popup_window('/access/' + flavor_number +'/batch_sheet/');
	newwindow.onload = function (e) {
		var batch_sheet_tbody = $(newwindow.document.getElementById('formula')).find('tbody')[0];
		jQuery('#flat-table tr').each( function(index, element) {
			if(index == 0) {
				return;
			}
			
			var cached_element = jQuery(element);
			var newrow = jQuery("<tr></tr>");
			var old_tds = jQuery(this).find('td');
			
//			var pin_cell = newwindow.document.createElement('td');
//			jQuery(pin_cell).addClass('abbrev').html(old_tds[1].textContent);
//			jQuery(newrow).append(pin_cell);
			
			var pin_num = '';
			var pin_cell = newwindow.document.createElement('td');
			jQuery(pin_cell).addClass('abbrev');

			
			jQuery(newrow).append(pin_cell);
			
			
			var na_cell = newwindow.document.createElement('td');
			jQuery(na_cell).addClass('abbrev').html(old_tds[NA_CELL].textContent);
			jQuery(newrow).append(na_cell);
			
			var name_cell = jQuery('<td><span class="ingredient-name"></span><span class="ingredient-name-2"></span><span class="sensitive"></span></td>');

			var pin_num = old_tds[PIN_CELL].textContent;
			if (old_tds[PREFIX_CELL].textContent != "") {
				var newname = old_tds[PREFIX_CELL].textContent + " " + old_tds[NAME_CELL].textContent;
			} else {
				var newname = old_tds[NAME_CELL].textContent;
			}
			
			jQuery(pin_cell).html(pin_num);
			jQuery(name_cell).find('.ingredient-name').html(newname);
			// jQuery(name_cell).find('.ingredient-name-2').html(old_name_cell.find('.ingredient-name-2').html());
			// jQuery(name_cell).find('.sensitive').html(old_name_cell.find('.sensitive').html());
			jQuery(newrow).append(name_cell);
			
			var pounds_cell = newwindow.document.createElement('td');
			var my_pounds = old_tds[AMOUNT_CELL].textContent
			var display_pounds = Math.round(my_pounds*1000)/1000;
			jQuery(pounds_cell).addClass('numerical').html(display_pounds.toFixed(3));
			jQuery(newrow).append(pounds_cell);
			
			var grams_cell = newwindow.document.createElement('td');
			var ogw = jQuery(this).data()['ogw'];
			var wf = jQuery(this).closest('div').find('#adjusted_weight').val();
			var display_grams = ogw * wf / 1000 * 453.59237;
			display_grams = Math.round(display_grams*100)/100;
			jQuery(grams_cell).addClass('numerical').html(display_grams.toFixed(2));
			jQuery(newrow).append(grams_cell);
			
			jQuery(newrow).append("<td></td><td></td><td></td><td></td><td></td>");
			jQuery(batch_sheet_tbody).append(newrow);
			
		});
		var total_weight = jQuery("#FormulaWeight").html();
		var batch_weight = jQuery("#actual_adjusted_weight").val();
		if (batch_weight === "") {
			batch_weight = total_weight;
		}
		var append_string = "<tr><td colspan=3></td><td colspan=2>Batch weight: " + batch_weight + "</td><td colspan=5></td></tr>";
		
		
		var batch_sheet_tfoot = $(newwindow.document.getElementById('formula')).find('tfoot')[0];
		jQuery(batch_sheet_tfoot).append(append_string);

		jQuery(newwindow.document).find("#formula").tablesorter({
			headers: {
					0: {
						sorter: 'digit'
					},
					1: {
						sorter: 'text'
					},
					2: {
						sorter: 'text'
					},
					3: {
						sorter: 'digit'
					},
					4: {
						sorter: 'digit'
					}
				}
		});
	};
}

function consolidated_review_popup(flavor_number) {
	newwindow = popup_window('/access/' + flavor_number +'/batch_sheet/');
	newwindow.onload = function (e) {
		var batch_sheet_tbody = $(newwindow.document.getElementById('formula')).find('tbody')[0];
		jQuery('#new_consolidated_table tr').each( function(index, element) {
			if(index == 0) {
				return;
			}
			var cached_element = jQuery(element);
			var newrow = jQuery("<tr></tr>");
			var old_tds = jQuery(this).find('td');
			
//			var pin_cell = newwindow.document.createElement('td');
//			jQuery(pin_cell).addClass('abbrev').html(old_tds[1].textContent);
//			jQuery(newrow).append(pin_cell);
			
			var pin_num = '';
			var pin_cell = newwindow.document.createElement('td');
			jQuery(pin_cell).addClass('abbrev');

			
			jQuery(newrow).append(pin_cell);
			
			
			var na_cell = newwindow.document.createElement('td');
			jQuery(na_cell).addClass('abbrev').html(old_tds[NA_CELL].textContent);
			jQuery(newrow).append(na_cell);
			
			var name_cell = jQuery('<td><span class="ingredient-name"></span><span class="ingredient-name-2"></span><span class="sensitive"></span></td>');
			var pin_num = old_tds[PIN_CELL].textContent;
			var newname = old_tds[NAME_CELL].textContent;
			
			
			jQuery(pin_cell).html(pin_num);
			jQuery(name_cell).find('.ingredient-name').html(newname);
			// jQuery(name_cell).find('.ingredient-name-2').html(old_name_cell.find('.ingredient-name-2').html());
			// jQuery(name_cell).find('.sensitive').html(old_name_cell.find('.sensitive').html());
			jQuery(newrow).append(name_cell);
			
			var pounds_cell = newwindow.document.createElement('td');
			var my_pounds = old_tds[AMOUNT_CELL].textContent
			var display_pounds = Math.round(my_pounds*1000)/1000;
			jQuery(pounds_cell).addClass('numerical').html(display_pounds.toFixed(3));
			jQuery(newrow).append(pounds_cell);
			
			var grams_cell = newwindow.document.createElement('td');
			var ogw = jQuery(this).data()['ogw'];
			var wf = jQuery(this).closest('div').find('#adjusted_weight').val();
			var display_grams = ogw * wf / 1000 * 453.59237;
			display_grams = Math.round(display_grams*100)/100;
			jQuery(grams_cell).addClass('numerical').html(display_grams.toFixed(2));
			jQuery(newrow).append(grams_cell);
			
			jQuery(newrow).append("<td></td><td></td><td></td><td></td><td></td>");
			jQuery(batch_sheet_tbody).append(newrow);
			
		});
		var total_weight = jQuery("#FormulaWeight").html();
		var batch_weight = jQuery("#actual_adjusted_weight").val();
		if (batch_weight === "") {
			batch_weight = total_weight;
		}
		var append_string = "<tr><td colspan=3></td><td colspan=2>Batch weight: " + batch_weight + "</td><td colspan=5></td></tr>";
		
		
		var batch_sheet_tfoot = $(newwindow.document.getElementById('formula')).find('tfoot')[0];
		jQuery(batch_sheet_tfoot).append(append_string);

		jQuery(newwindow.document).find("#formula").tablesorter({
			headers: {
					0: {
						sorter: 'digit'
					},
					1: {
						sorter: 'text'
					},
					2: {
						sorter: 'text'
					},
					3: {
						sorter: 'digit'
					},
					4: {
						sorter: 'digit'
					}
				}
		});
	};
}


function explosion_review_popup(flavor_number) {
	newwindow = popup_window('/access/' + flavor_number +'/batch_sheet/');
	accumulator = {};
	var wf = jQuery('#ft_review_table').find("#adjusted_weight").val() / 1000;
	var accumulate = function(ingredient_row, $ingredient_row) {
		if ( ingredient_row.dataset.ingredient_id in accumulator ) {
			accumulator[ingredient_row.dataset.ingredient_id].weight = accumulator[ingredient_row.dataset.ingredient_id].weight + parseFloat($ingredient_row.find('span.ftamount')[0].dataset.ogw);
		} else {
			var my_weight = parseFloat($ingredient_row.find('span.ftamount')[0].dataset.ogw * wf);
			var grams_eq = Math.round(my_weight * 453.59237 * 1000) / 1000;
			accumulator[ingredient_row.dataset.ingredient_id] = { 
				'weight': parseFloat($ingredient_row.find('span.ftamount')[0].dataset.ogw * wf),
				'grams_eq': grams_eq,
				'pin': ingredient_row.dataset.ingredient_pin,
				'name': ingredient_row.dataset.ingredient_name,
				'nat_art': ingredient_row.dataset.nat_art,
			};
		}
	};
	newwindow.onload = function (e) {
		jQuery('div.ft-expander-row:visible, div.ft-simple-row:visible').each( function (index,element) {
			var $this = $(this);
			if ( $this.hasClass('ft-expander-row') ) {
				var $next = $this.next();
				if ( $next.hasClass('ft-spacer') && $next.is(':hidden') ) {
					accumulate(this, $this);
				}
			} else {
				accumulate(this, $this);
			}
		});
		var batch_sheet_tbody = $(newwindow.document.getElementById('formula')).find('tbody')[0];
		var sorted_accumulator = [];
		for (k in accumulator) {
			sorted_accumulator.push(accumulator[k]);
		}
		sorted_accumulator.sort(function(a,b) {
			return b.weight - a.weight;
		});
		for (x in sorted_accumulator) {
			var y = sorted_accumulator[x];
			y.weight = Math.round(y.weight*1000)/1000;
			var newrow = jQuery("<tr></tr>");
			console.log(sorted_accumulator[x]);
			var pin_cell = newwindow.document.createElement('td');
			jQuery(pin_cell).addClass('abbrev').html(y.pin);
			jQuery(newrow).append(pin_cell);
			
			var na_cell = newwindow.document.createElement('td');
			jQuery(na_cell).addClass('abbrev').html(y.nat_art);
			jQuery(newrow).append(na_cell);
			
			var name_cell = newwindow.document.createElement('td');
			jQuery(name_cell).html(y.name);
			jQuery(newrow).append(name_cell);
			
			var pounds_cell = newwindow.document.createElement('td');
			var my_pounds = y.weight;
			jQuery(pounds_cell).addClass('numerical').html(my_pounds.toFixed(3));
			jQuery(newrow).append(pounds_cell);
			
			// var ogw = jQuery(this).data()['ogw'];
			// var wf = jQuery(this).closest('div').find('#adjusted_weight').val();
			// var display_grams = ogw * wf / 1000 * 453.59237;
			
			var grams_cell = newwindow.document.createElement('td');
			var display_grams = my_pounds * 453.59237
			display_grams = y.grams_eq;
			jQuery(grams_cell).addClass('numerical').html(display_grams);
			jQuery(newrow).append(grams_cell);
			
			jQuery(newrow).append("<td></td><td></td><td></td><td></td><td></td>");
			jQuery(batch_sheet_tbody).append(newrow);
		};
		
	};

}












function flavor_review_popup(flavor_number) {
	consolidate();
	newwindow = popup_window('/access/' + flavor_number +'/batch_sheet/');
	newwindow.onload = function (e) {
		var batch_sheet_tbody = $(newwindow.document.getElementById('formula')).find('tbody')[0];
		jQuery('#consolidated tr').each( function(index, element) {
			if(index == 0) {
				return;
			}
			var cached_element = jQuery(element);
			var newrow = jQuery("<tr></tr>");
			var old_tds = jQuery(this).find('td');
			
//			var pin_cell = newwindow.document.createElement('td');
//			jQuery(pin_cell).addClass('abbrev').html(old_tds[1].textContent);
//			jQuery(newrow).append(pin_cell);
			
			var pin_num = '';
			var pin_cell = newwindow.document.createElement('td');
			jQuery(pin_cell).addClass('abbrev');
			if(cached_element.hasClass('flavor')) {

			} else {
				pin_num = old_tds[1].textContent;
			}
			jQuery(pin_cell).html(pin_num);
			jQuery(newrow).append(pin_cell);
			
			
			var na_cell = newwindow.document.createElement('td');
			jQuery(na_cell).addClass('abbrev').html(old_tds[2].textContent);
			jQuery(newrow).append(na_cell);
			
			var name_cell = jQuery('<td><span class="ingredient-name"></span><span class="ingredient-name-2"></span><span class="sensitive"></span></td>');
			var old_name_cell = jQuery(old_tds[3]);
			var newname = "";
			
			// if (jQuery(old_tds[0]).parent()[0].className != "raw_material_tr") {
				// newname = old_tds[0].textContent + "-" + old_tds[1].textContent + " " + old_name_cell.html();
			// } else {
				// newname = old_name_cell.html();
				// pin_num = old_tds[1].textContent;
			// };
			
			
			
			if (jQuery(old_tds[0]).parent()[0].className.search("raw_material") == -1) {
				newname = old_tds[0].textContent + "-" + old_tds[1].textContent + " " + old_name_cell.find('.ingredient-name').html() + " " + old_tds[4].textContent;
			} else {
				newname = old_name_cell.find('.ingredient-name').html();
			};
			jQuery(name_cell).find('.ingredient-name').html(newname);
			jQuery(name_cell).find('.ingredient-name-2').html(old_name_cell.find('.ingredient-name-2').html());
			jQuery(name_cell).find('.sensitive').html(old_name_cell.find('.sensitive').html());
			jQuery(newrow).append(name_cell);
			
			var pounds_cell = newwindow.document.createElement('td');
			var my_pounds = old_tds[7].textContent
			var display_pounds = Math.round(my_pounds*1000)/1000;
			jQuery(pounds_cell).addClass('numerical').html(display_pounds.toFixed(3));
			jQuery(newrow).append(pounds_cell);
			
			var grams_cell = newwindow.document.createElement('td');
			var display_grams = my_pounds * 453.59237
			display_grams = Math.round(display_grams*100)/100;
			jQuery(grams_cell).addClass('numerical').html(display_grams.toFixed(2));
			jQuery(newrow).append(grams_cell);
			
			jQuery(newrow).append("<td></td><td></td><td></td><td></td><td></td>");
			jQuery(batch_sheet_tbody).append(newrow);
			
		});
		var total_weight = jQuery("#FormulaWeight").html();
		var batch_weight = jQuery("#actual_adjusted_weight").val();
		if (batch_weight === "") {
			batch_weight = total_weight;
		}

		var append_string = "<tr><td colspan=3></td><td colspan=2>Batch weight: " + batch_weight + "</td><td colspan=5></td></tr>";
		var batch_sheet_tfoot = $(newwindow.document.getElementById('formula')).find('tfoot')[0];
		jQuery(batch_sheet_tfoot).append(append_string);

		jQuery(newwindow.document).find("#formula").tablesorter({
			headers: {
					0: {
						sorter: 'digit'
					},
					1: {
						sorter: 'text'
					},
					2: {
						sorter: 'text'
					},
					3: {
						sorter: 'digit'
					},
					4: {
						sorter: 'digit'
					}
				}
		});
	};
}

// jQuery table2csv.js
jQuery.fn.divs2CSV = function(options){
	var options = jQuery.extend({
		separator: ',',
		header: [],
		delivery: 'popup' // popup, value
	}, options);
	var csvData = [];
	var headerArr = [];
	var el = this;
	
	//header
	var numCols = options.header.length;
	var tmpRow = []; // construct header avalible array
	if (numCols > 0) {
		for (var i = 0; i < numCols; i++) {
			tmpRow[tmpRow.length] = formatData(options.header[i]);
		}
	}
	else {
		$(el).filter(':visible').find('th').each(function(){
			if ($(this).css('display') != 'none') 
				tmpRow[tmpRow.length] = formatData($(this).html());
		});
	}
	
	// insert 6 blank rows at the top
	for (var x = 0; x < 6; x++) {
		csvData[csvData.length] = ''
	}
	row2CSV(tmpRow);
	
	// actual data
	$(el).find('tr').each(function(){
		var tmpRow = [];
		$(this).filter(':visible').find('td').each(function(){
			if ($(this).css('display') != 'none') 
				tmpRow[tmpRow.length] = formatData($(this).html());
		});
		row2CSV(tmpRow);
	});
	csvData[csvData.length] = ",,,,,,,=sum(h8:h" + csvData.length + "),=sum(i8:i" + csvData.length + ")";
	if (options.delivery == 'popup') {
		var mydata = csvData.join('\n');
		return popup(mydata);
	}
	else {
		var mydata = csvData.join('\n');
		return mydata;
	}
	
	function row2CSV(tmpRow){
		var tmp = tmpRow.join('') // to remove any blank rows
		// alert(tmp);
		if (tmpRow.length > 0 && tmp != '') {
			var mystr = tmpRow.join(options.separator);
			csvData[csvData.length] = mystr;
		}
	}
	function formatData(input){
		// replace " with â€œ
		var regexp = new RegExp(/["]/g);
		var output = input.replace(regexp, "â€œ");
		//HTML
		var regexp = new RegExp(/\<[^\<]+\>/g);
		var output = output.replace(regexp, "");
		if (output == "") 
			return '';
		return '"' + output + '"';
	}
	function popup(data){
		$("#exportdata").val(data);
		$("#exportform").submit();
		//return true;
	}
}

// jQuery table2csv.js
jQuery.fn.table2CSV = function(options) {
	var options = jQuery.extend({
		separator: ',',
		header: [],
		delivery: 'popup' // popup, value
	}, options);
	var csvData = [];
	var headerArr = [];
	var el = this;
	//header
	var numCols = options.header.length;
	var tmpRow = []; // construct header avalible array
	if (numCols > 0) {
		for (var i = 0; i < numCols; i++) {
			tmpRow[tmpRow.length] = formatData(options.header[i]);
		}
	}
	else {
		$(el).filter(':visible').find('th').each(function(){
			if ($(this).css('display') != 'none') 
				tmpRow[tmpRow.length] = formatData($(this).html());
		});
	}
	
	// insert 6 blank rows at the top
	for (var x = 0; x < 6; x++) {
		csvData[csvData.length] = ''
	}
	row2CSV(tmpRow);
	
	// actual data
	$(el).find('tr').each(function(){
		var tmpRow = [];
		$(this).filter(':visible').find('td').each(function(){
			if ($(this).css('display') != 'none') 
				tmpRow[tmpRow.length] = formatData($(this).html());
		});
		row2CSV(tmpRow);
	});
	csvData[csvData.length] = ",,,,,,,=sum(h8:h" + csvData.length + "),=sum(i8:i" + csvData.length + ")";
	if (options.delivery == 'popup') {
		var mydata = csvData.join('\n');
		return popup(mydata);
	}
	else {
		var mydata = csvData.join('\n');
		return mydata;
	}
	
	function row2CSV(tmpRow){
		var tmp = tmpRow.join('') // to remove any blank rows
		// alert(tmp);
		if (tmpRow.length > 0 && tmp != '') {
			var mystr = tmpRow.join(options.separator);
			csvData[csvData.length] = mystr;
		}
	}
	function formatData(input){
		// replace " with â€œ
		var regexp = new RegExp(/["]/g);
		var output = input.replace(regexp, "â€œ");
		//HTML
		var regexp = new RegExp(/\<[^\<]+\>/g);
		var output = output.replace(regexp, "");
		if (output == "") 
			return '';
		return '"' + output + '"';
	}
	function popup(data){
		$("#exportdata").val(data);
		$("#exportform").submit();
		//return true;
	}
}

jQuery(document).ready(function(){
	consolidate();	
	$("#exploded").treeTable();
	var menu_flavor_review = jQuery('#flavor_review_print_menu');
	menu_flavor_review.menu();
	jQuery('a[href$="FLAVOR_REVIEW_PRINT_MENU"]').click(function(event) {
		jQuery('#flavor_review_print_menu').show().position({
			my:'left top',
			at:'left bottom',
			of:event,
		});
		jQuery(document).one("click", function() {
			menu_flavor_review.hide();
		});
		return false;
	});

	
});