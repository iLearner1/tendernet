$(document).ready(function(){
    var data2;

    $('.form_buying_product').unbind("click").on('click', '.button.contact-button', function(e){
        e.preventDefault();
        var submit_btn = $('#submit_btn1');
        var tarif_type = submit_btn.data('user_tarif');
        var url = $('#form_buying_product').attr("action");
        var data = {};
        data["product_id"] = submit_btn.data("product_id1");
        data["user_id"] = submit_btn.data("user_id1");
        data["request_path"] = submit_btn.data("request_path1");
        data["csrfmiddlewaretoken"] = $('#form_buying_product [name="csrfmiddlewaretoken"]').val();
        data2 = data;
        data2['type'] = "form_buying_product";

        const key = `verify_data-${data2['user_id']}-${data2['product_id']}`;
        
        if(localStorage.getItem(key)) {
            return alert('Ваша заявка уже подана');
        }

        if(tarif_type.startsWith("EXP")) {
            $("#expert-feedback").modal("show");
            $("#expert-feedback .feedbackform").append(`<input type="hidden" class="feedbackform-value" value=${JSON.stringify({...data, url})} />`);
            return false;
        }
    
       
        
        if(tarif_type.startsWith("MN")) {
            $("#client-feedback").modal("show");
            $("#client-feedback .client-feedbackform").append(`<input type="hidden" class="cl-feedbackform-value" value=${JSON.stringify({...data, url})} />`);
            return false;
        }
    });


    $('.buying_doc').on('submit', function(e){
        e.preventDefault();
        var submit_btn = $('#submit_btn_doc');
        var data = {};
        
        data["product_id"] = submit_btn.data("product_id");
        data["user_id"] = submit_btn.data("user_id");
        data["request_path"] = submit_btn.data("request_path");
        data2 = data;
        data2['type'] = "buying_doc";
        
        const key = `verify_data-${data2['type']}-${data2['user_id']}-${data2['product_id']}`;
    
        if(!verifyUserClick(data2)) {
            
            if (confirm("Вы запрашиваете Аудит конкурсной документации. Он необходим, чтобы узнать какие ресурсы необходимы для участия в этом тендере.")) {
                alert('Спасибо за обращение. В ближайшее время с вами свяжется менеджер. А пока сохраните этот лот в Избранные.');
                var csrf_token = $('#buying_doc [name="csrfmiddlewaretoken"]').val();
                data["csrfmiddlewaretoken"] = csrf_token;
                var url = $('#buying_doc').attr("action");
              
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: data,
                    cache: true,
                    success: function (data) {
                        alert('Заявка на запрос документов отправлена');
                        localStorage.setItem(key, JSON.stringify(data2));
                        
                    },
                    error: function(){
                        console.log("error")
                    }
                });
            } else {
                return false;
            }

        }
        
    });

    
    //customizing front-table collaspe behavior
    $("#accordionExample").on("show.bs.collapse", function(e){
        var $clickedBtn = $(e.target).parent().addClass('border');
    });

    //customizing front-table collaspe behavior
    $("#accordionExample").on("hide.bs.collapse", function(e){
        var $clickedBtn =  $(e.target).parent().removeClass('border');
    });


    //when expert user user press ok btn in the model at article detail this action will triggred
    $("#expert-preference").off().on("click", function(e){
        e.preventDefault();

        const data = JSON.parse($(".feedbackform-value").val());
        const url = data.url;
        delete data.url;
        const formValue = $(".feedbackform").serializeArray() ?? [];
        const checkedValue = formValue.filter(val => {
                for(const item of formValue) {
                    if(item.name.startsWith("ch") && item.value === val.name) {
                        return true;
                    }
                }
        });

        data['expert_preference'] = JSON.stringify(checkedValue);
        $("#expert-feedback").modal("hide");
       
        if(!formValue.length) return;
        const key = `verify_data-${data['user_id']}-${data['product_id']}`;
        localStorage.setItem(key, 1)

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            cache: true,
            success: function (data) {
                alert('Заявка на участие отправлена');
                // const key = `verify_data-${data2['type']}-${data2['user_id']}-${data2['product_id']}`;
                // localStorage.setItem(key, JSON.stringify(data2));
                window.location.reload();
            },
            error: function(error){
                alert(error?.responseJSON?.message ?? 'Something went wrong please try again')
                console.log(error);
                console.log("error")
            }
        });
    })

    $("#client-preference").off().on("click", function(e){
        e.preventDefault();
        const data = JSON.parse($(".cl-feedbackform-value").val());
        const url = data.url;
        delete data.url;
        const formValue = $(".client-feedbackform :checkbox:checked").map(function(item){
            return {
                name: '',
                value: $(this).val()
            }
        }).get();
   
        data['expert_preference'] = JSON.stringify(formValue);
        $("#client-feedback").modal("hide");
        
        if(!formValue.length) return;
        const key = `verify_data-${data['user_id']}-${data['product_id']}`;
        localStorage.setItem(key, 1)

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            cache: true,
            success: function (data) {
                alert('Заявка на участие отправлена');
                window.location.reload();
            },
            error: function(error){
                alert(error?.responseJSON?.message ?? 'Something went wrong please try again')
                console.log(error);
                console.log("error")
            }
        });
    })

    $(".feedbackform input:checkbox").on("change", function(e) {
        if(this.checked) {
            $(`.${this.name}`).attr('disabled', false);
        } else {
            $(`.${this.name}`).attr('disabled', true);
        }
    });

    //remove user meta info that was saved localstorage before sending request
    $(document).on("click", ".request-delete", function(e) {
        e.preventDefault();
        const data = $(this).data();
        const key = `verify_data-${data['userId']}-${data['productId']}`;
        localStorage.removeItem(key);
        const $this = $(this);
        $this.parents().find('.request-delete-form').first().submit();
    });

    function verifyUserClick(data2) {
        const key = `verify_data-${data2['type']}-${data2['user_id']}-${data2['product_id']}`;
        if(localStorage.getItem(key)) {
            const verify_data = JSON.parse(localStorage.getItem(key));
            if(verify_data['product_id'] === data2['product_id'] && verify_data['user_id'] === data2['user_id'] &&  verify_data['type'] === data2['type']) {
                alert('Ваша заявка на данную услугу принята, пожалуйста дождитесь ответа специалиста');
                return true;
            } else {
              //  localStorage.setItem(key, JSON.stringify(data2));
            }
            return true;
        } else {
            return false;
            // localStorage.setItem(key, JSON.stringify(data2));
        }
    }

    $(document).on("click", ".access-error", (e) => {
        e.preventDefault();
        swal.fire({
            title: 'error',
            text: 'Вы должны сменить тариф на "Эксперт"',
            icon: 'error'
        })
    })

    function createButton(text,url) {
        if(text=='Авторизация'){
            return $(`<button id="signInRedirect" data-url="${url}" style="margin-bottom: 20px;padding: 6px 20px;background: #eb3547;color: #ffffff;border-radius: 6px;font-size:large;border:0px;">` + text + `</button>`);
        }else{
        return $(`<button id="signUpRedirect" data-url="${url}" style="padding: 6px 20px;background: #fff;color: #000;border: 1px solid #111c2b;border-radius: 6px;font-size:large; margin-bottom:15px;" > ` + text + `</button>`);
            }
    }

    $(document).on('click', "#signInRedirect", function() {
        let url  = this.getAttribute('data-url')
        if(url === '/accounts/login/?next=/lots/'){
            window.open(url);
            }else{
                window.location.href = url
            }

      });

      

    $(document).on('click', "#signUpRedirect", function() {
        let url  = this.getAttribute('data-url')
        if(url === '/accounts/login/?next=/lots/'){
            window.open('/signup');
        }else{
            window.location.href = '/signup'
        }   
      });

    $(document).on("click", ".un-authorized", function(e){

        e.preventDefault();

        const url = $(this).attr('href');
        
        const message = $(this).data('message') ? 'Вы должны авторизоваться' : 'Вы должны авторизоваться или зарегистрироваться в системе';
        const favorite = $(this).data('favorite');

        var buttons = $('<div>')
        .append(createButton('Авторизация',url).addClass('mt-3 mr-2')).append(createButton('Регистрация',url).addClass('mr-2'))


        // function() {
        //     alert('jere')
        // if(url === '/accounts/login/?next=/lots/'){
        // window.open(url);
        // }else{
        //     window.location.href = url
        // }
        // }
    //     function() {
    //         console.log('Register');
    //      if(url === '/accounts/login/?next=/lots/'){
    //      window.open('/signup');
    //      }else{
    //          window.location.href = '/signup'
    //      }        
    //  }

        Swal.fire({title:message,
                icon:'info',
                html: buttons,       
                showConfirmButton: false,
                showCancelButton: false,
                showCloseButton: true
           });

    });

});
