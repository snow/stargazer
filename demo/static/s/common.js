(function($) {
    window.s = {
        sync_load: function(uri){
            var data;
            
            $.ajax(uri, {
                success : function(txt) {
                    data = txt;
                },
                dataType : 'text',
                async : false
            });
            
            return data;
        }
    };

    s.load_com = function(com) {
        $.ajax('/com/' + com + '.html', {
            success : function(data) {
                document.write(data);
            },
            dataType : 'text',
            async : false
        });
    };
    
    /*
     * tools that only used in demo
     * --------------------------------
     */
    s.ex = {};
    
    s.ex.stream = {
        TYPE: {
            txt: 'txt',
            img: 'img',
            video: 'video',
            voice: 'voice'
        },
        
        templates: {
            item: false,
            item_s: false,
            txt: false,
            image: false,
        },
        
        get_item: function(type){
            var tpl = s.ex.stream.templates;
                
            if(!tpl['item']){
                tpl['item'] = s.sync_load('/com/stream/item_tpl.html');
            }
            
            if(!tpl[type]){
                tpl[type] = s.sync_load('/com/stream/type_tpl/' +
                                             type + '.html');
            }
            
            return tpl['item'].replace('${content}', tpl[type]);
        },
        
        get_item_s: function(type){
            var tpl = s.ex.stream.templates;
                
            if(!tpl['item_s']){
                tpl['item_s'] = s.sync_load('/com/stream/item_s_tpl.html');
            }
            
            if(!tpl[type]){
                tpl[type] = s.sync_load('/com/stream/type_tpl/' +
                                             type + '.html');
            }
            
            return tpl['item_s'].replace('${content}', tpl[type]);
        }
    };
    
    var msg_source = [
        '',
        'twitter',
        'g+',
        'flickr'
    ];

    s.ex.get_msg_source = function() {
        return msg_source[Math.floor(Math.random() * msg_source.length)]
    };
    
    var usernames = [
        'snowhs',
        '王小明',
        'goog',
        '成都商报 V'
    ];
    
    s.ex.get_username = function() {
        return usernames[Math.floor(Math.random() * usernames.length)]
    };
    
    s.ex.is_v = function() {
        return (66 < Math.random() * 100)?
               'V':
               ''
    };
    
    /*
     * tools for stream
     * ------------------
     */
    s.stream = {}

    s.stream.hate = function(anchor) {
        var j_stream_item = $(anchor).closest('.stream-item');

        j_stream_item.hide('fast', function() {
            $(this).remove();
        });
    };

    s.stream.like = function(anchor) {
        var j_anchor = $(anchor),
            cur_like_cnt = parseInt(j_anchor.text()), 
            j_stream_item = j_anchor.closest('.stream-item');
            
        if('NaN' === cur_like_cnt.toString())
        {
            cur_like_cnt = 0;
        }

        if(j_stream_item.hasClass('on')) {
            j_anchor.text(Math.max(0, cur_like_cnt-1));
            j_stream_item.removeClass('on');
        } else {            
            j_anchor.text(cur_like_cnt+1);
            j_stream_item.addClass('on');
        }
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
    
    s.init_addrbar = function(t, callback){
        j_bar = t;
        j_stat = j_bar.find('.stat');
        j_addr = j_bar.find('.addr');
        j_lat = j_bar.find('.lat');
        j_lng = j_bar.find('.lng');
            
        j_bar.bind('init_latlng', init_latlng).
            bind('done_latlng', function(){
                console && console.log('done_latlng');
                j_bar.trigger('init_addr');
            }).
            bind('init_addr', init_addr).
            bind('done_addressing', function(){
                console && console.log('done_addressing');
            });
            
        if('function' == typeof callback){
            j_bar.bind('done_addressing', callback);
        }    
        
        j_bar.trigger('init_latlng');
    }
})(jQuery);
