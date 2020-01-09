text = "";
types = document.getElementsByName('docheader');


name_dict = {
  'origin':'Country Of Origin',
  'specsheet':'Spec Sheet',
  'GMO':'GMO',
  'GPVC':'GMO Project Verified Cerificate',
  'LOG':'Letter Of Guarantee',
  'sds':'Safety Data Sheet',
  'kosher':'Kosher',
  'form20':'Form #020',
  'form20ar':'Form #020 Audit Report',
  'form20c':'Form #020 Certification',
  'halal':'Halal',
  'allergen':'Allergen',
  'nutri':'Nutritional Info',
  'COI':'Certificate of Insurance',
  'natural':'Natural',
  'vegan':'Vegan',
  'organic':'Organic',
  'COA':'Certificate of Analysis',
  'form40':'Form #040',
  'ingbreak':'Ingredient Breakdown'
};
// console.log(name_dict.toString());
// console.log(name_dict);
// console.log(name_dict['origin']);
for (i=0; i<types.length; i++){
  console.log(name_dict[String(types[i].innerHTML.textContent)]);

  // text = name_dict[types[i].innerText];
  console.log(types[i].innerHTML.textContent)
  // txt = document.createTextNode(text);
  // console.log(types[i].innerText);
  // types[i].innerHTML = text;
  // types[i].write(text);
  // var t = document.createTextNode(name_dict[types[i].innerText]);
  // console.log(name_dict[types[i].innerText]);
  // types[i].removeChild(types[i].firstChild);
  // types[i].appendChild(t);
  //
  // types[i].innerHTML = "";
  // types[i].innerHTML = name_dict[t];


}
// console.log("log");
// var timeout= null;
$('document').ready(function(){
  $('#correct_ing').keydown(function(){

    console.log( $(this).val() );
    var pin = $(this).val();

    $.ajax({
        url:'/access/dv_autocomplete/',
        minLength:1,
        data:{
          'pin':pin
        },
        dataType:'json',
        success:function(data){
          // setTimeout(function(){
              // var results = data['results']
              // console.log(data['results']);
              $("#correct_ing").autocomplete({
                source:data['results']
              });
              console.log(data['results']);
            // }, 1000);
        }
      });
    });
  });



function toggle_move_form() {
if(document.getElementById('move_doc').checked){
  document.getElementById('move_doc_form').style.display = "block";
}
else{
  document.getElementById('move_doc_form').style.display = "none";
}
}
function totalfatupdate() {
var poly = document.getElementById("id_FA_Poly").value;
var mono = document.getElementById("id_FA_Mono").value;
var satf = document.getElementById("id_FA_Sat").value;
var other = document.getElementById("id_TotalFat").value;
var totalFat = document.getElementById("total fat");

var total = parseFloat(poly) + parseFloat(mono) + parseFloat(satf) + parseFloat(other);
totalFat.innerHTML = total + " g";
}
function totalcarbupdate() {
var carbs = document.getElementById("id_Carbohydrt").value;
var sugars = document.getElementById("id_Sugars").value;
var fiber = document.getElementById("id_Fiber_TD").value;
var totalcarbs = document.getElementById("totalcarbs");

var total = parseFloat(carbs) + parseFloat(sugars) + parseFloat(fiber);
totalcarbs.innerHTML = total + " g";
}

function totalalcoholupdate() {
  var ethyl = document.getElementById("id_ethyl").value;
  var fusel = document.getElementById("id_fusel").value;
  var pg = document.getElementById("id_pg").value;
  var tc = document.getElementById("id_tri_citrate").value;
  var glycerin = document.getElementById("id_glycerin").value;
  var triacetin = document.getElementById("id_triacetin").value;
  var totalalcohol = document.getElementById("totalalcohol");

  var total = parseFloat(ethyl) + parseFloat(fusel) + parseFloat(pg)+ parseFloat(tc)+parseFloat(glycerin)+parseFloat(triacetin);
  totalalcohol.innerHTML = total;
}

function totalcalories(){

  var totalfat = parseFloat(document.getElementById("total fat").innerHTML);
  var protein = parseFloat(document.getElementById("id_Protein").value);
  var totalcarbs = parseFloat(document.getElementById("totalcarbs").innerHTML);
  // var alcohol = parseFloat(document.getElementById("id_AlcoholContent").value);
  var ethyl = document.getElementById("id_ethyl").value;
  var fusel = document.getElementById("id_fusel").value;
  var pg = document.getElementById("id_pg").value;
  var tc = document.getElementById("id_tri_citrate").value;
  var glycerin = document.getElementById("id_glycerin").value;
  var triacetin = document.getElementById("id_triacetin").value;
  // (fusel + ethyl) * 7 + pg * 4 + tri_ci * Decimal(3.7) + glycerin * 4 + triacetin * Decimal(1.7)
  var calories = 4 * (protein + totalcarbs) + 9 * totalfat + fusel * 7 + ethyl * 7 + pg * 4 + tc * 3.7 + glycerin * 4 + triacetin * 1.7;
  // console.log(calories);
  document.getElementById("calories").innerHTML = calories.toFixed(2);
  document.getElementById("id_Calories").value = calories.toFixed(2);
}

function checkTotalWeight(){
  var poly = parseFloat(document.getElementById("id_FA_Poly").value);
  var mono = parseFloat(document.getElementById("id_FA_Mono").value);
  var satf = parseFloat(document.getElementById("id_FA_Sat").value);
  var other = parseFloat(document.getElementById("id_TotalFat").value);
  var water = parseFloat(document.getElementById("id_Water").value);
  var protein = parseFloat(document.getElementById("id_Protein").value);
  var flavor = parseFloat(document.getElementById("id_FlavorContent").value);
  var alcohol = parseFloat(document.getElementById("totalalcohol").innerHTML);
  var carbs = parseFloat(document.getElementById("id_Carbohydrt").value);
  var sugar = parseFloat(document.getElementById("id_Sugars").value);
  var fiber = parseFloat(document.getElementById("id_Fiber_TD").value);
  var ash = parseFloat(document.getElementById("id_Ash").value);

  var t = poly + mono + satf + other + water + protein + flavor + alcohol + carbs + fiber + sugar + ash;
  document.getElementById("totalw").innerHTML = t;
  if(!(t < 102) || !(t > 98)){
      document.getElementById("totalw").classList.add("weighterror");
  }
  else{
      document.getElementById("totalw").classList.remove("weighterror");
  }

  console.log(document.getElementById('totalalcohol').innerHTML);
}

totalalcoholupdate();
totalfatupdate();
totalcarbupdate();
totalcalories();
checkTotalWeight();

document.getElementById("id_FA_Poly").addEventListener('input', function(){
totalfatupdate();
totalcalories();
});
document.getElementById("id_FA_Mono").addEventListener('input', function(){
totalfatupdate();
totalcalories();
});
document.getElementById("id_FA_Sat").addEventListener('input', function(){
totalfatupdate();
totalcalories();
});
document.getElementById("id_TotalFat").addEventListener('input', function(){
totalfatupdate();
totalcalories();
});
document.getElementById("id_Carbohydrt").addEventListener('input', function(){
    totalcarbupdate();
    totalcalories();
});
document.getElementById("id_Sugars").addEventListener('input', function(){
    totalcarbupdate();
    totalcalories();
});
document.getElementById("id_Fiber_TD").addEventListener('input', function(){
    totalcarbupdate();
    totalcalories();
});

document.getElementById("id_Protein").addEventListener('input', totalcalories);

document.getElementById("id_ethyl").addEventListener('input', function(){
totalalcoholupdate();
totalcalories();});
document.getElementById("id_fusel").addEventListener('input', function(){
totalalcoholupdate();
totalcalories();});
document.getElementById("id_pg").addEventListener('input', function(){
totalalcoholupdate();
totalcalories();});
document.getElementById("id_tri_citrate").addEventListener('input', function(){
totalalcoholupdate();
totalcalories();});
document.getElementById("id_glycerin").addEventListener('input', function(){
totalalcoholupdate();
totalcalories();});
document.getElementById("id_triacetin").addEventListener('input', function(){
totalalcoholupdate();
totalcalories();});

function check_is() {
if(document.getElementById('is').checked){
  document.getElementById('ingredient_statement').disabled = false;
}
else
  document.getElementById('ingredient_statement').disabled = true;
}

function addnutriclass() {
document.getElementById('reviewtable').classList.add('nutri');
}

function secondcas(){
document.getElementById('casrowbtn').disabled = true;
var row = document.createElement('tr');

var deletetd = document.createElement('td');
var inputtd = document.createElement('td');
var percenttd = document.createElement('td');
var deletebtn = document.createElement('BUTTON');
var casinput = document.createElement('input');
var caspercent = document.createElement('input');
var txt = document.createTextNode("Delete Row");
var percentnote = document.createTextNode("Enter percentage of second cas: ")

casinput.setAttribute('name', 'cas2');


caspercent.type='number';
caspercent.setAttribute('name', 'cas2percent');


deletebtn.type='button';
deletebtn.onclick = function(){
 this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);
 document.getElementById('casrowbtn').disabled = false;
 // checkrnumberduplicates();
}

casinput.required = true;
caspercent.required = true;
deletebtn.appendChild(txt);
deletetd.appendChild(deletebtn);
inputtd.appendChild(casinput);
percenttd.appendChild(percentnote);
percenttd.appendChild(caspercent);

row.appendChild(deletetd)
row.appendChild(inputtd)
row.appendChild(percenttd)

document.getElementById('cas').appendChild(row);

}

function disable_allergens(e){
var x = document.getElementsByClassName("allergen");
if (e.checked){
  for(i=0; i<x.length;i++){
    x[i].disabled = true;
  }
}
else{
  for(i=0; i<x.length;i++){
    x[i].disabled = false;
  }
}
}

function add_country(e){
  console.log('tada');
  var country_row = document.getElementById('country_dl_row');
  var clone = country_row.cloneNode(true);
  var deletebtn = document.createElement('BUTTON');
  var txt = document.createTextNode("Delete Row");
  var deletetd = document.createElement('td');

  deletebtn.type='button';
  deletebtn.onclick = function(){
    this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);
   // checkrnumberduplicates();
  }

  deletebtn.appendChild(txt);
  deletetd.appendChild(deletebtn);
  // clone.childNodes[0] = deletetd;
  clone.replaceChild(deletetd, clone.childNodes[0]);
  var table = document.getElementById('origin_table');
  table.appendChild(clone);

}

$('.flexdatalist').flexdatalist({
     minLength: 1
});

function toggle() {
  var input = document.getElementById('product_list_id');
  var flexlist_input = document.getElementById('product_list_id-flexdatalist');
  console.log('click');
  input.disabled = !input.disabled;
  flexlist_input.disabled = !flexlist_input.disabled;
  flexlist_input.required = !flexlist_input.required
}
