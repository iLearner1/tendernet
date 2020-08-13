$(document).ready(function() {
    document.querySelector('#id_itemZakup').onchange = function() {
        var val = document.querySelector('#id_itemZakup').value;
        console.log(val);
        if(val == "services" || val == "job")
        {
            document.querySelector('#id_count').value = '1';
        }
        else
        {
            document.querySelector('#id_count').value = '';
        }
    }
});


