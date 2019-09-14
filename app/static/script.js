$(document).ready(function() {

                $(".subcategory").hide();
                $(".name-segment").hide();

                $(".cat-header").click(function() {
                    children=$(this).siblings('div')
                    $(children).slideToggle();});
                
                $(".subcat-header").click(function() {
                    children=$(this).siblings('div')
                    $(children).slideToggle();});

});



