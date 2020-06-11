$(document).ready(function(){
    var form = $('#form_buying_product');
    console.log(form);


    form.on('submit', function(e){
        e.preventDefault();
        var submit_btn = $('#submit_btn1');

        var data = {};
        data["product_id"] = submit_btn.data("product_id1");
        data["user_id"] = submit_btn.data("user_id1");
        data["request_path"] = submit_btn.data("request_path1");
         data["csrfmiddlewaretoken"] = $('#form_buying_product [name="csrfmiddlewaretoken"]').val();

         var url = $('#form_buying_product').attr("action");

        console.log(data);

         $.ajax({
             url: url,
             type: 'POST',
             data: data,
             cache: true,
             success: function (data) {
                 alert('Заявка на участие отправлена');
             },
             error: function(){
                 console.log("error")
             }
         });
    });


    var form = $('#buying_doc');
    console.log(form);

    form.on('submit', function(e){
        e.preventDefault();

        var submit_btn = $('#submit_btn_doc');

        var data = {};
        data["product_id"] = submit_btn.data("product_id");
        data["user_id"] = submit_btn.data("user_id");
        data["request_path"] = submit_btn.data("request_path");

         var csrf_token = $('#buying_doc [name="csrfmiddlewaretoken"]').val();
         data["csrfmiddlewaretoken"] = csrf_token;

         var url = form.attr("action");

        console.log(data);

         $.ajax({
             url: url,
             type: 'POST',
             data: data,
             cache: true,
             success: function (data) {
                 alert('Заявка на запрос документов отправлена');
             },
             error: function(){
                 console.log("error")
             }
         });
    });
});