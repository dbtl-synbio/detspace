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
       $.ajax({
          url:"static/website/files/producibles_names.csv",
          dataType:"text",
          success:function(data)
          {
             var producible_data = data.split(/\r?\n|\r/);
             var table_data = '<table class="table table-bordered table-condensed table-hover" id="producibles_table">';
             for(var count=0; count < producible_data.length; count++)
             {
                var cell_data = producible_data[count].split(";");
                table_data += '<tr>'+'id="producible"';
                for(var cell_count=0; cell_count < cell_data.length; cell_count++)
                {
                   if(count == 0)
                   {
                         table_data += '<th>'+cell_data[cell_count]+'</th>';
                   }
                   else
                   {
                         table_data += '<td>'+'<a href="#" onclick="ddlselect_prod()">'+cell_data[cell_count]+'<a/>'+'</td>';
                   }
                }
                table_data += '</tr>';
             }
             table_data += '</table>';
             $('#producibles_table').html(table_data);
          }
       });
    });

 });

  