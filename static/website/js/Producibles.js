var div =document.getElementById('dialogo_prod');
var display =0;

function hideShow_prod() 
{
    if(display == 1)
    {
        $("#dialogo_prod").dialog("close");
        display = 1;
    }
    else
    {
        $("#dialogo_prod").dialog("open");
        display = 0;
    }
}