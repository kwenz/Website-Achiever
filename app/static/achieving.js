function add_achievement(id){
                    
                var id_box="#box"+id
                var id_inner="#inner"+id
                var id_btac="#btac"+id
                var id_bttd="#bttd"+id
                var id_btrm="#btrm"+id

                var cl_box=$(id_box).attr('class')

                $(id_box).removeClass(cl_box).addClass('achieved')

                if(cl_box=="todo"){
                    $(id_inner).removeClass('inner-td').addClass('inner-ac')
                }
                else{
                    $(id_inner).removeClass('inner-na').addClass('inner-ac')
                }

                $(id_btac).attr('disabled','disabled')
                $(id_bttd).attr('disabled',false)
                $(id_btrm).attr('disabled',false)


                $.post("{{url_for('add_achievement')}}",{
                        id:id,
                    }).done(function(data){
                        
                        $('#header-abs').text("Absolute progress: "+data.pr_str+"%")
                        $('#header-rel').text("Relative progress: "+data.pr_des_str+"%")
                        $('#bar-abs').css('width',data.pr_str+"%").css('aria-valuenow',data.pr);
                        $('#bar-abs').text(data.pr_str+"%");

                        $('#bar-rel').css('width',data.pr_des_str+"%").css('aria-valuenow',data.pr_des);
                        $('#bar-rel').text(data.pr_des_str+"%");

                        $('#user-total').text(data.tot);
                        $('#ach-count').text(data.ach_count);
                        $('#user-des').text(data.des);

                        if(data.unlock){
                            $.each(data.unlock,function(index,value){
                                var idb="#box"+value
                                var idba="#btac"+value
                                var idbt="#bttd"+value

                                $(idb).removeClass('disabled');
                                $(idba).attr('disabled',false);
                                $(idbt).attr('disabled',false);

                            });
                        }

                        if(data.lock){
                            $.each(data.lock,function(index,value){
                                var idi="#inner"+value
                                var idbr="#btrm"+value
                                var idbt="#bttd"+value

                                $(idi).removeClass('inner-ac').addClass('inner-ac-deep');
                                $(idbr).attr('disabled','disabled');
                                $(idbt).attr('disabled','disabled');

                            });
                        }
                        
                    });
                };


        function remove_achievement(id){

                var id_box="#box"+id
                var id_inner="#inner"+id
                var id_btac="#btac"+id
                var id_bttd="#bttd"+id
                var id_btrm="#btrm"+id

                var cl_box=$(id_box).attr('class')

                $(id_box).removeClass(cl_box).addClass('not-achieved')

                if(cl_box=="todo"){
                    $(id_inner).removeClass('inner-td').addClass('inner-na')
                }
                else{
                    $(id_inner).removeClass('inner-ac').addClass('inner-na')
                }

                $(id_btac).attr('disabled',false)
                $(id_bttd).attr('disabled',false)
                $(id_btrm).attr('disabled','disabled')

                $.post("{{url_for('remove_achievement')}}",{
                        id:id,
                }).done(function(data){
                        
                            $('#header-abs').text("Absolute progress: "+data.pr_str+"%")
                            $('#header-rel').text("Relative progress: "+data.pr_des_str+"%")
                            $('#bar-abs').css('width',data.pr_str+"%").css('aria-valuenow',data.pr);
                            $('#bar-abs').text(data.pr_str+"%");

                            $('#bar-rel').css('width',data.pr_des_str+"%").css('aria-valuenow',data.pr_des);
                            $('#bar-rel').text(data.pr_des_str+"%");

                            $('#user-total').text(data.tot);
                            $('#ach-count').text(data.ach_count);
                            $('#user-des').text(data.des);

                        if(data.unlock){
                            $.each(data.unlock,function(index,value){
                                var idi="#inner"+value
                                var idbr="#btrm"+value
                                var idbt="#bttd"+value

                                $(idi).removeClass('inner-ac-deep').addClass('inner-ac');
                                $(idbr).attr('disabled',false);
                                $(idbt).attr('disabled',false);

                            });
                        }

                        if(data.lock){
                            $.each(data.lock,function(index,value){
                                var idb="#box"+value
                                var idba="#btac"+value
                                var idbt="#bttd"+value

                                $(idb).addClass('disabled');
                                $(idba).attr('disabled','disabled');
                                $(idbt).attr('disabled','disabled');

                            });
                        }


                    });
                };

        function add_todo(id){


                var id_box="#box"+id
                var id_inner="#inner"+id
                var id_btac="#btac"+id
                var id_bttd="#bttd"+id
                var id_btrm="#btrm"+id

                var cl_box=$(id_box).attr('class')

                $(id_box).removeClass(cl_box).addClass('todo')

                if(cl_box=="achieved"){
                    $(id_inner).removeClass('inner-ac').addClass('inner-td')
                }
                else{
                    $(id_inner).removeClass('inner-na').addClass('inner-td')
                }

                $(id_btac).attr('disabled',false)
                $(id_bttd).attr('disabled','disabled')
                $(id_btrm).attr('disabled',false)


                    $.post("{{url_for('add_todo')}}",{
                        id:id,
                    }).done(function(data){
            
                            $('#header-abs').text("Absolute progress: "+data.pr_str+"%")
                            $('#header-rel').text("Relative progress: "+data.pr_des_str+"%")
                            $('#bar-abs').css('width',data.pr_str+"%").css('aria-valuenow',data.pr);
                            $('#bar-abs').text(data.pr_str+"%");

                            $('#bar-rel').css('width',data.pr_des_str+"%").css('aria-valuenow',data.pr_des);
                            $('#bar-rel').text(data.pr_des_str+"%");

                            $('#user-total').text(data.tot);
                            $('#ach-count').text(data.ach_count);
                            $('#user-des').text(data.des);

                        if(data.lock){
                            if(data.avd){
                                $.each(data.lock,function(index,value){
                                    var idb="#box"+value
                                    var idba="#btac"+value
                                    var idbt="#bttd"+value

                                    $(idb).addClass('disabled');
                                    $(idba).attr('disabled','disabled');
                                    $(idbt).attr('disabled','disabled');
                                });
                            }else{
                                $.each(data.lock,function(index,value){
                                    var idi="#inner"+value
                                    var idbr="#btrm"+value
                                    var idbt="#bttd"+value

                                    $(idi).removeClass('inner-ac').addClass('inner-ac-deep');
                                    $(idbr).attr('disabled','disabled');
                                    $(idbt).attr('disabled','disabled');
                                });
                            }
                        }

                    });
                };