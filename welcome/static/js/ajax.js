//////////// Show/hide a part of the site
function switch_brick(brick_selection, url_to_request, url_to_show){
    $('.site-brick').hide();
    //console.log('selection is ' + brick_selection)
    //console.log('data state is ' + $(brick_selection).data('state'))
    //if($(brick_selection).html()=='')
    $(brick_selection).show();
    history.pushState(null, '', url_to_show);
    if($(brick_selection).data('state') == 'empty') {
        $(brick_selection).html("<img class='img-responsive' src='/static/img/preloader.gif' alt='in progress...'></img>");
        $.get(url_to_request, {}, function(data){
            $(brick_selection).html(data);
            $(brick_selection).data('state', 'got')
            //console.log('now data-state is ' + $(brick_selection).data('state'))
        });
    }
    $('.in').collapse('hide');
}
//////////// Click on the cart in the right-top corner
$('body').on('click', '#cart', function(event){
    //console.log('cart clicked')
    switch_brick('#block-cart','/cart_async/', '/cart');
});
//////////// Click on the menu section
$('body').on('click', '#menu_section_1', function(event){
    switch_brick('#block-products-hot', "/products_hot_async/", '/products_hot')
});
$('body').on('click', '#menu_section_2', function(event){
    switch_brick('#block-products-cold', "/products_cold_async/", '/products_cold')
});
$('body').on('click', '#menu_section_3', function(event){
    switch_brick('#block-products-office', "/products_office_async/", '/products_office')
});
///////////// Menu sections dropdown on hover
$('ul.nav li.dropdown').hover(function() {
  $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(500);
}, function() {
  $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(500);
});
///////////// Initial setup: Switch on popovers, select delivery on checkout
$(document).ready(function(){
    initialSetup();
});

function initialSetup(){
    $('[data-toggle="popover"]').popover();
    /*$('a[rel="popover"]').popover({
        html: true,
        trigger: 'hover',
        placement: 'bottom',
        content: function(){return '<img src="'+$(this).data('img') + '" />';}
    });*/
    $('input[type=radio][name=delivery]').change(function(){
        //console.log('выбрана доставка: ' + this.id)
        if(this.id == 'shipping_needed'){
            $('#form_shipping').show()
            $('#form_pickup').hide()
        }else{
            $('#form_shipping').hide()
            $('#form_pickup').show()
        }
    })
    $('input[type=radio][name=lunch_type]').change(function(){
        //console.log($('input[name=lunch_type]:checked').attr('id'));
        calc_office();
    });
    $('#id_people_number').bind('input', function(event){
        calc_office();
    });
    $('#checkout-form').on('submit', function(event){
        event.preventDefault();
        //console.log("checkout form submitted!")  // sanity check
        if(data_is_valid()){
            send_order();
            switch_brick('#block-thankyou','/thankyou_async/', '/thankyou');
        }
    });
    $('#feedback-form').on('submit', function(event){
        event.preventDefault();
        $('#feedback-result-message').html("<img class='img-responsive' src='/static/img/preloader.gif' alt='in progress...'></img>");
        //console.log("form submitted!");  // sanity check
        send_feedback();
    });
    /*$('#news-header').click(function(){
        console.log('clicked!')
        current_date = new Date();
        console.log(current_date.toLocaleDateString());
        console.log();
    });*/

}

$(document).ajaxComplete(function() {
    initialSetup();
});

$('body').on('click', '#delivery', function(event){
    switch_brick('#block-delivery', "/delivery_async/", "/delivery")
});

$('body').on('click', '#logo', function(event){
    //product_id = $(this).attr('id').substring(7)
    //console.log('logo clicked')
    $('.site-brick').hide();
    if($('#block-carousel').data('state') == 'empty')
        $.get("/carousel_async/", {}, function(data) {
            $('#block-carousel').html(data);
            $('#block-carousel').data('state', 'got');
        });
    //console.log('carousel is done');
    $('#block-carousel').show();
    if($('#block-news').data('state') == 'empty')
        $.get("/news_async/", {}, function(data) {
            $('#block-news').html(data);
            $('#block-news').data('state', 'got');
        });
    //console.log('news is done');
    $('#block-news').show();
    if($('#block-about').data('state') == 'empty')
        $.get("/about_async/", {}, function(data) {
            $('#block-about').html(data);
            $('#block-about').data('state', 'got');
        });
    //console.log('about is done');
    $('#block-about').show();
    //$('#myCarousel').carousel('cycle');
    history.pushState(null, '', '/');
});

$('body').on('click', '#vacancies', function(event){
    switch_brick('#block-vacancy', '/vacancy_async/', '/vacancy')
});

$('body').on('click', '#contacts', function(event){
    switch_brick('#block-contacts', '/contacts_async/', '/contacts')
});
//////////// Remove a product from the cart
$('body').on('click', '.glyph-remove-product', function(event){
    product_id = $(this).attr('id').substring(7)
    //console.log('remove clicked with id=' + product_id)
    $.get("/remove_from_cart/", {'product_id' : product_id}, function(data) {
            //console.log(json); // log the returned json to the console
            $('#cart_content').html(data.content_html);
            $('#cart_date').html(data.cart_date);
            $('#number_in_cart').html(data.new_amount);
            //console.log("success"); // another sanity check
        });
});
///////////// Add a product to the cart
$('body').on('click', '.current_cart', function(){
    product_id = $(this).attr('id').substring(14)
    the_date = $(this).attr('id').substring(5,13)
    amount = $('#product_' + the_date + '_' + product_id).val()
    if(the_date == '00000000')
        the_date=null
    //console.log('cart clicked with id=' + product_id)
    //console.log('amount=' + amount + ', the date=' + the_date)
    $.ajax({
        url : "/add_to_cart/", // the endpoint
        type : "GET", // http method
        data : { 'product_id' : product_id,
            'amount': amount,
            'date': the_date
         }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            //console.log('result=' + json.result); // log the returned json to the console
            if(json.result == 0){
                $('#date-in-cart').html(json.cart_date);
                $("#wrong-date-dialog").modal()
            }
            $('#number_in_cart').html(json.new_amount);
            $('#cart_content').html(json.content_html);
            $('#cart_date').html(json.cart_date);
            //console.log("cart_date=" + json.cart_date); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#debug').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            //console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
});
///////////// Proceed to checkout
$('body').on('click', '#go-checkout', function(){
    switch_brick('#block-checkout','/checkout_async/', '/checkout');
})

//////////// Cookie warning
$('body').on('click', '#cookie-warning-button', function(event){
    $.get("/cookie_confirm/", function(){
        $('#block-cookie_warning').hide();
        //console.log('block hidden')
    });
});

//////////// Checkout ////////////////

/*$('body').on('click', '#confirm-order-button', function(event){
    event.preventDefault();
    if(data_is_valid()){
        send_order();
        switch_brick('#block-thankyou','/thankyou_async/', '/thankyou');
    }
});*/

function data_is_valid() {
    //console.log('checking the data...')
    if(!required_fields_all()){
        //console.log('fields are NOT OK');
        show_message('Заполните обязательные поля');
        return false;
    }else if(!$('#user-agreed').prop('checked')) {
            //console.log("we don't see the check!")
            show_message('Вы не согласились с условиями и на обработку перс. данных');
            return false;
        }else{
            delivery_time = new Date($('#id_delivery_time_2').data("DateTimePicker").date())
            default_delivery_time = new Date($('#id_delivery_time_2').data("DateTimePicker").defaultDate())
        }
    show_message('');
    return true;
}

function required_fields_all(){
    client_name_OK = required_field_single('id_client_name_2', 'id_client_name_group');
    sender_OK = required_field_single('id_sender_2', 'id_sender_group');
    phone_OK = required_field_single('id_phone_2', 'id_phone_group');
    if($('#id_address_2').is(':visible'))
        delivery_OK = required_field_single('id_address_2', 'id_address_group');
    else delivery_OK = true;
    /*else
        delivery_OK = required_field_single('id_cafe_2', 'id_cafe_group');*/
    if($('#id_delivery_time_2').data("DateTimePicker").date() == null) {
        $('#id_delivery_time_group').addClass("has-error");
        $('#id_delivery_time_group').addClass("has-feedback");
        //console.log(field_id + ' is empty')
        time_OK = false;
    }else{
        $('#id_delivery_time_group').removeClass("has-error");
        $('#id_delivery_time_group').removeClass("has-feedback");
        time_OK = true;
        //console.log(field_id + ' is OK')
    }
    //time_OK = required_field_single('id_delivery_time_2', 'id_delivery_time_group');
    //console.log('retvalue is ' + client_name_OK && sender_OK && phone_OK && delivery_OK && time_OK);
    return client_name_OK && sender_OK && phone_OK && delivery_OK && time_OK;
}

function required_field_single(field_id, group_id){
    if($('#' + field_id).val() == '') {
        $('#' + group_id).addClass("has-error");
        $('#' + group_id).addClass("has-feedback");
        //console.log(field_id + ' is empty');
        return false;
    }else{
        $('#' + group_id).removeClass("has-error");
        $('#' + group_id).removeClass("has-feedback");
        //console.log(field_id + ' is OK');
        return true;
    }
}

function show_message(msg){
    if(msg == '')
        $('#message-to-user').hide()
    else {
        $('#message-to-user').html(msg)
        $('#message-to-user').show()
    }
}

function send_order() {
    //console.log('function called');
    //console.log($('#id_message').val())
    //console.log(grecaptcha.getResponse());
    timestamp = $('#id_delivery_time_2').data("DateTimePicker").date()
    //console.log('date is ' + $('#id_delivery_time_2').data("DateTimePicker").date())
    //console.log('and ' + timestamp)
    delivery_time = new Date(timestamp),
    delivery_time_str = delivery_time.toLocaleDateString() + ' ' + delivery_time.toLocaleTimeString().substring(0, 5)
    //console.log(delivery_time);
    //console.log('is visible = ' + $('#id_address_2').is(':visible'))
    $.ajax({
        url : "/order/", // the endpoint
        type : "POST", // http method
        data : { 'client_name' : $('#id_client_name_2').val(),
            'sender': $('#id_sender_2').val(),
            'phone': $('#id_phone_2').val(),
            'address_visible': $('#id_address_2').is(':visible'),
            'address': $('#id_address_2').val(),
            'address2': $('#id_address2_2').val(),
            'cafe_to_pick_up': $('#id_cafe_2').val(),
            'delivery_time': delivery_time_str,//$('#id_delivery_time_2').data("DateTimePicker").date(),
            'flatware':  $('#id_flatware_2').val(),
            'hot_delivery':  $('#id_hot_delivery_2').prop('checked'),
            'payment_method': $('input[name=payment]:checked', '#payment-form').attr('id')
         }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            if(json.result>0){
                //$('#id_client_name').val(''); // remove the value from the input
                //$('#id_sender').val(''); // remove the value from the input
                //$('#id_phone').val(''); // remove the value from the input
                //$('#id_message').val(''); // remove the value from the input
                show_message(json.message);
               }
            else
                show_message(json.message);
            //console.log(json); // log the returned json to the console
            //console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            show_message('Oops! We have encountered an error: ' + errmsg); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
}
//////////// Calculator for office menu
function calc_office(){
    people_number = $('#id_people_number').val();
    //console.log('people_number=' + people_number)
    if($('input[name=lunch_type]:checked').attr('id') == 'id_lunch_light')
        multiplier = 1
    else
        multiplier = 2
    plates_number = Math.ceil(people_number * multiplier / 8 );
    sandwiches_per_person = Math.round(plates_number * 20 / people_number * 10) / 10;
    $('#plates_number').html(plates_number);
    $('#sandwiches_per_person').html(sandwiches_per_person)
    if(people_number < 3)
        $('#too_little').show()
    else
        $('#too_little').hide()
}
//////////// Feedback
function send_feedback() {
    //console.log('function called');
    //console.log($('#id_message').val())
    //console.log(grecaptcha.getResponse());
    $.ajax({
        url : "/feedback/", // the endpoint
        type : "POST", // http method
        data : { 'client_name' : $('#id_client_name').val(),
            'sender': $('#id_sender').val(),
            'phone': $('#id_phone').val(),
            'message': $('#id_message').val(),
            'captcha': grecaptcha.getResponse()//$(".g-recaptcha")
         }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            if(json.result>0){
                $('#id_client_name').val(''); // remove the value from the input
                $('#id_sender').val(''); // remove the value from the input
                $('#id_phone').val(''); // remove the value from the input
                $('#id_message').val(''); // remove the value from the input
                $('#feedback-result-message').html('<div class="alert alert-success">' + json.message + '</div>')
               }
            else
                $('#feedback-result-message').html('<div class="alert alert-danger">' + json.message + '</div>')
            //console.log(json); // log the returned json to the console
            //console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            //console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
}

$(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
