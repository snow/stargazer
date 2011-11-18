/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.s = {}
    
    s_doc = $(document);
})(jQuery);

/*
 * tools for stream
 * ------------------
 */
(function($) {
    
    s.stream = {}
    
    var j_lat,
        j_lng,
        j_stream,
        sorter,
        CONTENT_URI = '/post/load/'+sorter+'/',
        csrf;
    
    s.stream.init = function(){
        csrf = $('[name=csrfmiddlewaretoken]').val();
        j_bar = $('#addrbar');
        j_lat = j_bar.find('.lat');
        j_lng = j_bar.find('.lng');
        j_stream = $('#stream');
        sorter = j_stream.attr('sorter');
        
        CONTENT_URI = '/post/load/'+sorter+'/';
        
        j_stream.delegate('.stream-item .ban', 'click', function() {
            s.stream.ban(this);
        }).delegate('.stream-item .like', 'click', function() {
            s.stream.like(this);
        });
        
        s.stream.load();
    };
    
    s.stream.load = function(content_uri){
        $.ajax(CONTENT_URI, {
            'type': 'GET',
            'data': {
                'lat': j_lat.text(),
                'lng': j_lng.text()
            },
            'success': function(data){
                j_stream.append(data);
            }
        });
    };

    s.stream.ban = function(anchor) {
        var j_stream_item = $(anchor).closest('.stream-item'),
            id = j_stream_item.attr('sid');
        
        return $.ajax('/post/ban/',{
            'type': 'POST',
            'data':{'id':id, 'csrfmiddlewaretoken': csrf},
            'success': function(data){
                j_stream_item.hide('fast', function() {
                    $(this).remove();
                });
            },
            'dataType':'json'
        });

    };

    s.stream.like = function(anchor) {
        var j_anchor = $(anchor),
            cur_like_cnt = parseInt(j_anchor.text()), 
            j_stream_item = j_anchor.closest('.stream-item'),
            id = j_stream_item.attr('sid');
            
        if('NaN' === cur_like_cnt.toString())
        {
            cur_like_cnt = 0;
        }

        return $.ajax('/post/like/',{
            'type': 'POST',
            'data':{'id':id, 'csrfmiddlewaretoken': csrf},
            'success': function(data){
                if(j_stream_item.hasClass('on')) {
                    j_anchor.text(Math.max(0, cur_like_cnt-1));
                    j_stream_item.removeClass('on');
                } else {            
                    j_anchor.text(cur_like_cnt+1);
                    j_stream_item.addClass('on');
                }
            },
            'dataType':'json'
        });
    };
})(jQuery);

/**
 * init latlng and address
 * -----------------------------
 */
(function($){
    var j_bar,
        j_stat,
        j_addr,
        j_lat,
        j_lng,
        
        j_form,
        j_flat,
        j_flng,
        j_faddr,
        
        NO_GEO_MSG = '该设备不支持定位 /. .\\',
        
        LOCATING_MSG = '正在获取经纬度...',
        FAILED_LOCATION_MSG = '获取位置失败 /. .\\',
        ADDRESSING_MSG = '正在获取地址...',
        FAILED_ADDRESSING_MSG = '获取地址失败 /. .\\';    
    
    function init_latlng(){
        if('' !== j_lat.text() && '' !== j_lng.text()){
            console && console.log('latlng already initialised');
            j_bar.trigger('done_latlng');
            return;
        }
        
        if(navigator.geolocation) {
            j_stat.addClass('locating').text(LOCATING_MSG);
            console && console.log('acquiring location');
          
            navigator.geolocation.getCurrentPosition(function(position) { 
                j_stat.removeClass('locating').empty();
                console && console.log('got location from browser');
                
                j_lat.text(position.coords.latitude)
                j_lng.text(position.coords.longitude)
                
                // due with lattidue and longitude that more than 7 float point
                // e.g. safari has 8
                $.each([j_lat, j_lng], function(idx, j_f){
                    var str = j_f.text(),
                        pidx = str.indexOf('.');
                        
                    j_f.text(str.substr(0, pidx+8));
                });
                
                if(position.address){
                    console && console.log('got address from browser');
                    
                    addr = ''
                    if(position.address.street){
                        addr += position.address.street
                    }
                    if(position.address.streetNumber){
                        addr += ' ' + position.address.streetNumber
                    }
                  
                    j_addr.text(addr)
                }
                
                j_bar.trigger('done_latlng');
            }, function() {
                j_stat.removeClass('locating').addClass('failed').
                    text(FAILED_LOCATION_MSG);
            });
        } else {
            j_stat.addClass('failed').text(NO_GEO_MSG);
        }
    }
    
    function after_latlng(){
        if(j_form){
            j_flat.val(j_lat.text());
            j_flng.val(j_lng.text());
        }
        
        console && console.log('done_latlng');
        
        j_bar.trigger('init_addr');
    }
    
    function init_addr(){
        if('' !== j_addr.text()){
            console && console.log('address already initialised');
            j_bar.trigger('done_addressing');
            return;
        }
        
        j_stat.addClass('addressing').text(ADDRESSING_MSG);
        console && console.log('acquiring address from server');
        $.ajax('/utils/latlng2addr', {
            data: {
                'lat': j_lat.text(),
                'lng': j_lng.text()
            },
            success: function(data){
                j_stat.removeClass('addressing').empty();
                j_addr.text(data);
                j_bar.trigger('done_addressing');
            },
            error: function(){
                j_stat.removeClass('addressing').addClass('failed').
                    text(FAILED_ADDRESSING_MSG);
            },
            dataType: 'text'});
    }
    
    function after_addr(){
        if(j_form){
            j_faddr.val(j_addr.text());
        }
        console && console.log('done_addressing');
    }
    
    s.init_addrbar = function(params){
        j_bar = $('#addrbar');
        
        if(0 === j_bar.length){
            return;
        }
        
        j_stat = j_bar.find('.stat');
        j_addr = j_bar.find('.addr');
        j_lat = j_bar.find('.lat');
        j_lng = j_bar.find('.lng');
        
        if(params.form){
            j_form = params.form,
            j_flat = j_form.find('[name=latitude]'),
            j_flng = j_form.find('[name=longitude]'),
            j_faddr = j_form.find('[name=address]');
        }
            
        j_bar.bind('init_latlng', init_latlng).
            bind('done_latlng', after_latlng).
            bind('init_addr', init_addr).
            bind('done_addressing', after_addr);
            
        if('function' == typeof params.callback){
            j_bar.bind('done_addressing', params.callback);
        }    
        
        j_bar.trigger('init_latlng');
    }
})(jQuery);

jQuery(function($){
    // hide address bar on android built-in browser
    s_doc.scrollTop(1);
    s_doc.scrollTop(0);
    
    $('form').each(function(idx, el){
        var j_form = $(el);
        j_form.find('[type=text],[type=password], textarea').
            width(j_form.width()-10);
    });
});
