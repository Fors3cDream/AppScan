$('#safety').delegate('.item-list li','click',function(){
    var $safetyDetails = $(this).children('.safety-details');
    $('.safety-details').slideUp('fast');
    if($safetyDetails.css('display') == 'block'){
        $safetyDetails.slideUp('fast');
    }else{
        $(this).children('.safety-details').slideDown('fast');
    }
})


var safetyJson = {
        'success' : ['fa-check-square','data-success'],
        'danger' : ['fa-exclamation-circle','data-danger'],
        'general' : ['fa-exclamation-circle' ,'data-general'],
        'manual' : ['fa-close (alias)','data-manual']

    };

$('#safety .label-data').each(function(i){
    var labelData = $('#safety .label-data').eq(i).text();
    switch(labelData){
        case '安全':
            labelStyle($(this),safetyJson['success'][0],safetyJson['success'][1]);
            break;
        case '危险':
            labelStyle($(this),safetyJson['danger'][0],safetyJson['danger'][1]);
            break;
        case '一般':
            labelStyle($(this),safetyJson['general'][0],safetyJson['general'][1]);
            break;
        case '手工检测':
                labelStyle($(this),safetyJson['manual'][0],safetyJson['manual'][1]);
                break;
    }
})

function labelStyle(obj,icon,color){
    obj.attr({'data-icon':icon,'data-color':color});
    obj.addClass(obj.attr('data-color'));
    obj.parent('.item-row').children('i').eq(0).addClass(obj.attr('data-icon')).addClass(obj.attr('data-color'));
}

