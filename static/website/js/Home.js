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

  