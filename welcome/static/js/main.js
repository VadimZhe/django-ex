function switch_brick(brick_selection, url_to_request, url_to_show){
    $('.site-brick').hide();
    if($(brick_selection).html()=='')
        $.get(url_to_request, {}, function(data){
            $(brick_selection).html(data);
        });
    $(brick_selection).show();
    history.pushState(null, '', url_to_show);
}