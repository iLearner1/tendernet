$(document).ready(function(){
    var form = $('#form_buying_product');
    console.log(form);


    form.on('submit', function(e){
        e.preventDefault();
        var submit_btn = $('#submit_btn1');
        var product_id1 =  submit_btn.data("product_id1");
        var user_id1  = submit_btn.data("user_name1");
        console.log(product_id1 );
        console.log(user_id1 );

        var data = {};
        data.product_id1 = product_id1;
        data.user_id1 = user_id1;
         var csrf_token = $('#form_buying_product [name="csrfmiddlewaretoken"]').val();
         data["csrfmiddlewaretoken"] = csrf_token;

         var url = $('#form_buying_product').attr("action");

        console.log(data)
         $.ajax({
             url: url,
             type: 'POST',
             data: data,
             cache: true,
             success: function (data) {
                 alert('Заявка на участие отправлена')



             },
             error: function(){
                 console.log("error")
             }
         })







    });


    var form = $('#buying_doc');
    console.log(form);

    form.on('submit', function(e){
        e.preventDefault();
        console.log('123');
        var submit_btn = $('#submit_btn_doc');
        var product_id =  submit_btn.data("product_id");
        var user_id  = submit_btn.data("user_name");
        console.log(product_id );
        console.log(user_id);

        var data = {};
        data.product_id = product_id;
        data.user_id = user_id;
         var csrf_token = $('#buying_doc [name="csrfmiddlewaretoken"]').val();
         data["csrfmiddlewaretoken"] = csrf_token;

         var url = form.attr("action");

        console.log(data)
         $.ajax({
             url: url,
             type: 'POST',
             data: data,
             cache: true,
             success: function (data) {
                 alert('Заявка на запрос документов отправлена')


             },
             error: function(){
                 console.log("error")
             }
         })







    });















});