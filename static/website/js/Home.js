//const Home = () => {

    const handleClick = () => {
        console.log('You have selected Acinetobacter baumannii AYE');
    }


    var div =document.getElementById('dialogo');
    var display =0;
    
    function hideShow() 
    {
        if(display == 1)
        {
            $("#dialogo").dialog("close");
            display = 1;
        }
        else
        {
            $("#dialogo").dialog("open");
            display = 0;
        }
    }
//}

//Chassis dialog//
$(document).ready(function(){
    $("#dialogo").dialog({
     modal: true,
     title: "Chassis",
     width: 250,
     minWidth: 200,
     maxWidth: 400, 
     //show: "fold", 
     hide: "scale",
     autoOpen: false
 });
});

//Conversion of the producibles table from csv to html//
$(document).ready(function(){
   $('#producibles').click(function(){
     var det_id=$("#txtvalue_det").attr("det_id");
     if(det_id==undefined){
        det_id=""
     }
      $.ajax({
         url:"/api/prod/"+det_id,
         dataType:"json",
         success:function(data)
         {
            //var detectable_data = data.split(/\r?\n|\r/);

              var table_data = '<table class="table table-bordered table-condensed table-hover" id="producibles_table">';
              $.each( data, function( index,val ) {
                 table_data += '<tr'+'id="producible>"';
                 table_data +="<td id='" + val["ID"] + "'>" + '<a href="#" onclick="ddlselect_prod()">'+ val["Name"] + '</a>'+"</td>";
                 table_data +="<td>" + val["SMILES"] + "</td>";
                 table_data += '</tr>';
               });
              table_data += '</table>';
              $('#producibles_table').html(table_data);
           ;}//success
      });
   });

});

// Button action that shows the network.json//
 function show_pathways() {
    $.getScript("static/website/files/network.json");
    run_viz();
    console.log("static/website/files/network.json")
    }

    
//Conversion of the detectables table from csv to html//
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

               var table_data = '<table class="table table-bordered table-condensed table-hover" id="detectables_table">';
               $.each( data, function( index,val ) {
                  table_data += '<tr'+'id="detectable>"';
                  table_data +="<td id='" + val["ID"] + "'>" + '<a href="#" onclick="ddlselect_det()">'+ val["Name"] + '</a>'+"</td>";
                  table_data +="<td>" + val["SMILES"] + "</td>";
                  table_data += '</tr>';
                });
               table_data += '</table>';
               $('#detectables_table').html(table_data);
            ;}//success
       });
    });

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
                         table_data += '<td>'+'<a href="#" onclick="ddlselect_det()">'+cell_data[cell_count]+'<a/>'+'</td>';
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


 // Code for the insertion of a search window //

// Reading of the .json file//


//const data = function Func() => {
   //fetch("static/website/files/prod_det.json")
   //.then(response => response.json())
   //.then(data => console.log(data))
   //.then(json => return JSON.stringify(json))
   //import dataJson from "static/website/files/prod_det.json" 
       //.then((res) => {
        //d_data=res.json();
        //console.log(d_data)
       //return res.json();
   //}
   //.then((data) => console.log(data));
   //return d_data


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
 
var product_chosen=-1
var detect_chosen=-1