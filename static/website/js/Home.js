var network = {};
var pathways_info = {};
var orgid="ECOLI";
var div =document.getElementById('dialogo');
var display =0;

$(document).ready(function(){
   var det_name= document.getElementById("txtvalue_det").value;
   var prod_name= document.getElementById("txtvalue_prod").value;
         document.getElementById("det_selected").value=det_name;
         document.getElementById("prod_selected").value=prod_name;
   if ( ($("#txtvalue_prod").attr("prod_id") != undefined && $("#txtvalue_det").attr("det_id") != undefined) &&
      ($("#txtvalue_prod").attr("prod_id") != '' && $("#txtvalue_det").attr("det_id") != '') ) { //In case the url is in format .../detect/prod/det
      product_chosen = $("#txtvalue_prod").attr("prod_id");
      detect_chosen = $("#txtvalue_det").attr("det_id");
      $.ajax ({
         url:"/api/net/"+String(product_chosen)+"/"+String(detect_chosen),
         dataType: "script",
         success: function() {
            run_viz(network, pathways_info);
            refresh_layout();
            // orgid = document.getElementById("txtvalue").orgid
            // if (document.getElementById(orgid) == null){
            //    orgid = 'ECOLI';
            //    url = '/detect/'+String(product_chosen)+'/'+String(detect_chosen)+'/'+orgid;
            //    $(location).attr('href', url);
            // }
            in_chassis(orgid);
            document.getElementById("pathway_selection").style.visibility="visible";
            document.getElementById("info_pair").style.visibility="visible";
            document.getElementById("info").style.borderLeftStyle="hidden";
            document.getElementById("info").style.borderBottomStyle="hidden";
            document.getElementById("info").style.borderTopStyle="hidden";
            document.getElementById("info").style.borderRightStyle="hidden";
            document.getElementById("info").style.width="0%";
            count_intermediate();
         }
      });   
   } else { //This values are the default example
      product_chosen = '';
      detect_chosen = '';
      // document.getElementById("txtvalue_prod").value = "Ethylene glycol"
      // document.getElementById("txtvalue_det").value = 'Methylmalonyl-coa'
      document.getElementById("txtvalue").value = 'Escherichia Coli'
      document.getElementById("txtvalue").orgid = 'ECOLI'
      // $.getScript("/api/net/"+String(product_chosen)+"/"+String(detect_chosen));
      document.getElementById("intro").style.display="block";
   }
   $.ajax ({
      url:"/api/prod/"+detect_chosen,
      dataType:"json",
      success:function(data){
         $.each(data, function(index, val){
            if (val["ID"] == product_chosen){
               product_name = val["Name"];
               document.getElementById("txtvalue_prod").value=product_name;
               document.getElementById("prod_selected").value=product_name;
            }
         });
      }
   });
   $.ajax ({
      url:"/api/det/"+product_chosen,
      dataType:"json",
      success:function(data){
         $.each(data, function(index, val){
            if (val["ID"] == detect_chosen){
               detect_name = val["Name"];
               document.getElementById("txtvalue_det").value=detect_name;
               document.getElementById("det_selected").value=detect_name;
            }
         });
      }
   });
});

// Chassis dialog selection function
$(document).ready(function(){
   $("#list-container").change(function() {
   var d=document.getElementById("list-container");
   var displaytext=d.options[d.selectedIndex].text;
   orgid = $(this).children(":selected").attr("id");
   document.getElementById("txtvalue").value=displaytext;
   $("#dialogo").dialog("close");
   $("#dialogo_apps").dialog("close");
   var display =1;
   });
});

$(document).ready(function(){
   $("#list-container_apps").change(function() {
   var d=document.getElementById("list-container_apps");
   var displaytext=d.options[d.selectedIndex].text;
   orgid = $(this).children(":selected").attr("id");
   document.getElementById("txtvalue").value=displaytext;
   $("#dialogo_apps").dialog("close");
   $("#dialogo").dialog("close");
   var display =1;
   });
});

function hideShow() {
   $("#dialogo").dialog({
      modal: false,
      title: "Chassis",
      width: 400,
      minWidth: 200,
      maxWidth: 500, 
      height:180,
      //show: "fold", 
      hide: "scale",
      autoOpen: false
   });
   if(display == 1){
      $("#dialogo").dialog("close");
      display = 1;
   } else {
      $("#dialogo").dialog("open");
      display = 0;
   }

   $("#dialogo_apps").dialog({
      modal: false,
      title: "Chassis applications",
      width: 250,
      minWidth: 200,
      maxWidth: 500, 
      //show: "fold", 
      hide: "scale",
      autoOpen: false,
      position: { at: "center bottom" },
   });
   if(display == 1){
      $("#dialogo_apps").dialog("close");
      display = 1;
   } else {
      $("#dialogo_apps").dialog("open");
      display = 0;
   }
}

//Conversion of the chassis table from json to html//
$(document).ready(function(){
   $('#Chassis').click(function(){
      $.ajax({
         url:"/api/chassis/",
         dataType:"json",
         success:function(data)
         {
              var table_data = '<table class="table table-bordered table-condensed table-hover" id="chassis_table">';
              table_data += '<tr'+'id=chassis>';
              table_data +="<th>" + "Organism" + "</th>";
              table_data +="<th>" + "ORGID" + "</th>";
              $.each( data, function( index,val ) {
                 table_data += '<tr'+'id="chassis>"';
                 table_data += "<td>" + val["Organism"] + "</td>";
                 table_data +="<td id='" + val["Organism"] + "'>" + '<a href="#" onclick="ddlselect()">'+ val["Orgid"] + '</a>'+"</td>";
                 table_data += '</tr>';
               });
              table_data += '</table>';
              $('#chassis_table').html(table_data);
           ;}//success
      });
   });
});

//Conversion of the producibles table from json to html//
$(document).ready(function(){
   $('#producibles').click(function(){
     var det_id=$("#txtvalue_det").attr("det_id");
     var det_name=$("#txtvalue_det").attr("det_id");
     if(det_id==undefined){
        det_id=""
     }
      $.ajax({
         url:"/api/prod/"+det_id,
         dataType:"json",
         success:function(data){
            //var detectable_data = data.split(/\r?\n|\r/);
            var table_base = $('<table class="table table-striped  table-hover tablesorter" id="producibles_table"></table>');
            let field_names = ['Compound name', 'SMILES', 'Effectors', 'Selected pathways'];
            let field_classes = ['name_head', 'smiles_head', 'effectors_head', 'selected_pathways_head'];
            let table_row = $('<tr class="customBackground"></tr>');
            for (let i=0; i<field_names.length;i++){
               let value = field_names[i];
               table_row.append($('<th class="align-middle"'+field_classes[i]+'"></th>').html(value));
            }
            table_base.append($('<thead class= "thead-light"></thead>').append(table_row));
            
            let table_body = $('<tbody ></tbody>');
            $.each( data, function( index,val ) {
               let table_row = $('<tr></tr>');
               table_row.append($("<td class='click_prod' id='" + val["ID"] + "'>" + '<a href="#">'+ val["Name"] + '</a>'+"</td>"));
               table_row.append($("<td class='smiles'>" + val["SMILES"] + "</td>"));
               table_row.append($("<td class='effectors'>" + val["Effectors"] + "</td>"));
               if (val["Selected"]==0){
                  table_row.append($("<td class='pathways'>" + "0"+" / "+ val["Pathways"] + "</td>"));
                }
                else {
                  table_row.append($("<td class='pathways'>" + val["Selected"]+" / "+val["Pathways"] + "</td>"));
                }
               table_body.append(table_row);
            });
            table_base.append(table_body);
            $('#producibles_modal_table').html(table_base);
            //Incluye el ordenamiento alfabético
            $("#producibles_table").tablesorter(
               {sortList: [[0,0], [1,0],[2,0], [3,0],[4,0]]}, 
               {arrows: { 
                  up:  '&uArr;', 
                  down: '&dArr;' }
              },
              {widgets: ['zebra']},
               {widgetOptions : {
                  zebra : ["even", "odd"],
              }}
               );

            //Incluye el stripe
            // $('#producibles_table').stripe();

            // Fetch the table data and store it in an array
            var tableData = $('#producibles_table td:nth-child(1)').map(function() {
               return $(this).text();
               }).get();

            // Initialize the Autocomplete widget with search functionality
            $('#searchInput_prod').autocomplete({
            appendTo: "#suggesstion-box_producibles",
            source: tableData,
            minLength: 1, // Minimum characters required to trigger autocomplete
            select: function(event, ui) {

            // Get the selected value from the table and show the corresponding rows
               var selectedValue = ui.item.value;
               var matchingRows = [];
               $.each(tableData, function(index, rowData) {
                  if (rowData.includes(selectedValue)) {
                  matchingRows.push(index);
                  }
               });
               $('#producibles_table tbody tr').hide();
               $.each(matchingRows, function(index, rowIdx) {
                  $('#producibles_table tbody tr:eq(' + rowIdx + ')').show();
               });
            },
            response: function(event, ui) {
               if (ui.content.length === 0) {
                  // No match found, display a message or perform additional actions
                  $('#noResultMessage_prod').text('No matching results found.');
               } else {
                  $('#noResultMessage_prod').empty();
               }
            }
            });
            $("td.click_prod").click(function(){
               var produc = $(this);
              // var det_chosen = ;
               document.getElementById("txtvalue_prod").value=produc.text();
               $("#txtvalue_prod").attr("prod_id",produc.attr("id"));
               $('#modal_producibles').modal('hide');
               $('.modal-backdrop').remove();
               product_chosen = $("#txtvalue_prod").attr("prod_id");
               detect_chosen = $("#txtvalue_det").attr("det_id");
               if(product_chosen!="" && detect_chosen!=""){
                  $.getScript("/api/net/"+String(product_chosen)+"/"+String(detect_chosen));
               }
            });
           }
      });
      $.ajax ({
         url:"/api/det/"+product_chosen,
         dataType:"json",
         success:function(data){
            $.each(data, function(index, val){
               if (val["ID"] == detect_chosen){
                  detect_name = val["Name"];
                  document.getElementById("det_selected").value=detect_name;
               }
            });
         }
      });
   });
});

// jQuery.fn.stripe = function() {
//    $(this).find('tr').removeClass('even odd').filter(':odd').addClass('odd').end().find('tr:even').addClass('even');
// }

   
 
   // Clear the search input and show all rows when the input field is empty
   $('#searchInput_prod').on('input', function() {
     var searchValue = $(this).val().trim();
     if (searchValue === '') {
       $('#producibles_table tbody tr').show();
       $('#noResultMessage').empty();
     }
   });


// Button action that shows the network.json//
function show_pathways() {
   if (String(product_chosen) != '' && String(detect_chosen) != ''){
      url = '/detect/'+String(product_chosen)+'/'+String(detect_chosen)+'/'+orgid;
      $(location).attr('href', url);
   } else {
      document.getElementById("no_choosen_error").style.visibility = "visible";
   }
}

function close_interaction(){
   document.getElementById('interaction').style.display="none";
   document.getElementById('open_interaction_bttn').style.display='block';
   screen_size = screen.width;
   document.getElementById('cy').style.width = String(screen_size)+'px';
   document.getElementById('cy').style.float = 'left';
}

function open_interaction(){
   document.getElementById('interaction').style.display="block";
   document.getElementById('open_interaction_bttn').style.display='none';
   document.getElementById('cy').style.width = "1500px";
   document.getElementById('cy').style.float = 'right';
}
    
//Conversion of the detectables table from json to html//
$(document).ready(function(){
    $('#detectables').click(function(){
      var prod_id=$("#txtvalue_prod").attr("prod_id");
      if(prod_id==undefined){
         prod_id=""
      }
       $.ajax({
          url:"/api/det/"+prod_id,
          dataType:"json",
          success:function(data)
          {
             //var detectable_data = data.split(/\r?\n|\r/);

             let table_base = $('<table class="table table-striped table-hover tablesorter" id="detectables_table"></table>');
             let field_names = ['Compound name', 'SMILES', 'Products', 'Selected pathways'];
             let table_row = $('<tr></tr>');
             for (let i=0; i<field_names.length;i++){
                let value = field_names[i];
                table_row.append($('<th class="align-middle"></th>').html(value));
             }
             table_base.append($('<thead class= "thead-light"></thead>').append(table_row));
             
             let table_body = $('<tbody ></tbody>');
             $.each( data, function( index,val ) {
                let table_row = $('<tr></tr>');
                table_row.append($("<td class='click_det' id='" + val["ID"] + "'>" + '<a href="#">'+ val["Name"] + '</a>'+"</td>"));
                table_row.append($("<td class='smiles'>" + val["SMILES"] + "</td>"));
                table_row.append($("<td class='products'>" + val["Products"] + "</td>"));
                if (val["Selected"]==0){
                  table_row.append($("<td class='pathways'>" + val["Pathways"] + "</td>"));
                }
                else {
                  table_row.append($("<td class='pathways'>" + val["Selected"]+" / "+val["Pathways"] + "</td>"));
                }
                table_body.append(table_row);
             });
             table_base.append(table_body);
             $('#detectables_modal_table').html(table_base);
             //Incluye el ordenamiento alfabético
            $("#detectables_table").tablesorter( {sortList: [[0,0], [1,0]]} );
            //Incluye el stripe
            // $('#detectables_table').stripe();

            // Fetch the table data and store it in an array
            var tableData = $('#detectables_table td:nth-child(1)').map(function() {
               return $(this).text();
               }).get();

            // Initialize the Autocomplete widget with search functionality
            $('#searchInput_det').autocomplete({
            appendTo: "#suggesstion-box_detectables",
            source: tableData,
            minLength: 1, // Minimum characters required to trigger autocomplete
            select: function(event, ui) {

            // Get the selected value from the table and show the corresponding rows
               var selectedValue = ui.item.value;
               var matchingRows = [];
               $.each(tableData, function(index, rowData) {
                  if (rowData.includes(selectedValue)) {
                  matchingRows.push(index);
                  }
               });
               $('#detectables_table tbody tr').hide();
               $.each(matchingRows, function(index, rowIdx) {
                  $('#detectables_table tbody tr:eq(' + rowIdx + ')').show();
               });
            },
            response: function(event, ui) {
               if (ui.content.length === 0) {
                  // No match found, display a message or perform additional actions
                  $('#noResultMessage_det').text('No matching results found.');
               } else {
                  $('#noResultMessage_det').empty();
               }
            }
            });
            $("td.click_det").click(function(){
               var detec = $(this);
              // var det_chosen = ;
              document.getElementById("txtvalue_det").value=detec.text();
              $("#txtvalue_det").attr("det_id",detec.attr("id"));
              $('#modal_detectables').modal('hide');
              $('.modal-backdrop').remove();
              product_chosen= $("#txtvalue_prod").attr("prod_id");
              detect_chosen= $("#txtvalue_det").attr("det_id");
              if(product_chosen!="" && detect_chosen!=""){
                 $.getScript("/api/net/"+String(product_chosen)+"/"+String(detect_chosen));
               }
            });
            ;}//success
       });
       $.ajax ({
         url:"/api/prod/"+detect_chosen,
         dataType:"json",
         success:function(data){
            $.each(data, function(index, val){
               if (val["ID"] == product_chosen){
                  product_name = val["Name"];
                  document.getElementById("prod_selected").value=product_name;
               }
            });
         }
      });
    });
 });


    // Clear the search input and show all rows when the input field is empty
    $('#searchInput_det').on('input', function() {
      var searchValue = $(this).val().trim();
      if (searchValue === '') {
        $('#detectables_table tbody tr').show();
        $('#noResultMessage').empty();
      }
    });
 
//Conversion of the pairs table from csv to html//
$(document).ready(function(){
    $('#pairs').click(function(){
       $.ajax({
          url:"static/website/files/pairs_pathways.csv",
          dataType:"text",
          success:function(data)
          {
             var pairs_data = data.split(/\r?\n|\r/);
             var table_data = '<table class="table table-bordered table-condensed table-hover" id="detectables_table">';
             for(var count=0; count < pairs_data.length; count++)
             {
                var cell_data = pairs_data[count].split(";");
                table_data += '<tr>'+'id="pair"';
                for(var cell_count=0; cell_count < cell_data.length; cell_count++)
                {
                   if(count == 0)
                   {
                         table_data += '<th>'+cell_data[cell_count]+'</th>';
                   }
                   else
                   {
                         table_data += '<td>'+'<a href="#">'+cell_data[cell_count]+'<a/>'+'</td>';
                   }
                }
                table_data += '</tr>';
             }
             table_data += '</table>';
             $('#detectables_table').html(table_data);
          }
       });
    });

 });

function get_det(){
   $.getJSON( "/api/det/", function( data ) {
      var items = [];
      $.each( data, function( index,val ) {
        items.push( "<li id='" + val["ID"] + "'>" + val["Name"] + "</li>" );
      });
     
      $( "<ul/>", {
        "class": "my-new-list",
        html: items.join( "" )
      }).appendTo( "body" );
    });
   }
 
function delete_chassis() {
   document.getElementById("txtvalue").orgid="";
   document.getElementById("txtvalue").value="";
   document.getElementById("list-container").value="";
   document.getElementById("list-container_apps").value="";
   $("#list-container").children(":selected").attr("id","");
   $("#list-container_apps").children(":selected").attr("id","");
   }
 
function delete_producible() {
   document.getElementById("txtvalue_prod").value="";
   $("#txtvalue_prod").attr("prod_id","");
   document.getElementById("prod_selected").value="";
   product_chosen = '';
   }

function delete_auto_producible() {
   document.getElementById("searchInput_prod").value="";
   $('#noResultMessage_prod').empty();
   }

function delete_detectable() {
   document.getElementById("txtvalue_det").value="";
   $("#txtvalue_det").attr("det_id","");
   document.getElementById("det_selected").value="";
   detect_chosen = '';
   }

function delete_auto_detectable() {
   document.getElementById("searchInput_det").value="";
   $('#noResultMessage_det').empty();
   }
