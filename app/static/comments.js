$(document).ready(function(){

    
    $('.col-md-9>div').each(function(){
        if($(this).height()<$(this).prop('scrollHeight')){
        $(this).parent().append("<br><a style='float:right;font-size:12px;cursor:pointer;'>Read more</a>")
        };
    });
    

    $(".col-md-9>a").click(function(){

        text_container=$(this).siblings('div');
        container=$(this).parent().parent().parent();

        text_container_height=text_container.css('height');
        container_height=container.css('height');

        if($(this).text()=="Read more"){
            
            text_container.css('height','auto').css('min-height',text_container_height);
            container.css('height','auto').css('min-height',container_height);

            $(this).text('Back')
        }
        else{

            text_container.css('height','85px').css('min-height',0);
            container.css('height','180px').css('min-height',0);

            $(this).text('Read more')
        };
    });
});