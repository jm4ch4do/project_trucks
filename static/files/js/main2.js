/**
* Purpose: Fixes for adaptation of template to Trucks System
* Author: José Raúl Machado Fernández
*/

/*--------------------------------------------------------------
# TABLE IN WORKDAYS
--------------------------------------------------------------*/

var hide_string = "d-none"

function sumTable(){

  var tableBody = window.document.getElementsByTagName("tbody").item(0);

  var sum = 0
  var i
  var col_to_sum = 2
  var ini_row = 0
  var last_row = tableBody.rows.length - 1;
  

  for (i=ini_row; i<last_row; i++){
    var row = tableBody.rows[i];

    if (row.className.includes(hide_string)){
      continue;
    }

    var cell = row.cells[col_to_sum];			
    var TextNode = cell.childNodes.item(0);
    var value = parseFloat(TextNode.data)

    var sum = sum + value
  }

  var sum_field = window.document.getElementById("summary-value");
  sum_field.innerHTML = sum;

}

function hideRow(current_row){

  var tableBody = window.document.getElementsByTagName("tbody").item(0);
  var row = tableBody.rows[current_row];
  row.classList.add(hide_string);
  sumTable()
}

function hideRowsAbove(current_row){

  var tableBody = window.document.getElementsByTagName("tbody").item(0);
  var i

  for (i=0; i<current_row; i++){
    var row = tableBody.rows[i];
    row.classList.add(hide_string);
  }

  sumTable()
}

function hideRowsBelow(current_row){

  var tableBody = window.document.getElementsByTagName("tbody").item(0);
  var last_row = tableBody.rows.length - 1;
  var i

  for (i=current_row+1; i<last_row; i++){
    var row = tableBody.rows[i];
    row.classList.add(hide_string);
  }

  sumTable()
}

function showAllRows(){

var tableBody = window.document.getElementsByTagName("tbody").item(0);

var i
var ini_row = 0
var last_row = tableBody.rows.length - 1;

for (i=ini_row; i<last_row; i++){
  var row = tableBody.rows[i];

  if (row.className.includes(hide_string)){
    row.classList.remove(hide_string);
  }

}

sumTable()

}
