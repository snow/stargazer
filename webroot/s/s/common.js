/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.s = {}
    
    s.j_doc = $(document);
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
    var NO_GEO_MSG = '该设备不支持定位 /. .\\',
        LOCATING_MSG = '正在获取经纬度...',
        FAILED_LOCATION_MSG = '获取位置失败 /. .\\',
        ADDRESSING_MSG = '正在获取地址...',
        FAILED_ADDRESSING_MSG = '获取地址失败 /. .\\',
        
        LATLNG_TO_ADDR_API = '/utils/latlng2addr/';
        
    s.geo = {};
    
    /*s.geo.initialized = false;
    s.geo.lat = false;
    s.geo.lng = false;
    s.geo.addr = false;*/
    
    s.geo.E_NOT_SUPPORT = 's-geo-not_support';
    s.geo.E_LATLNG_START = 's-geo-latlng_start';
    s.geo.E_LATLNG_DONE = 's-geo-latlng_done';
    s.geo.E_LATLNG_FAIL = 's-geo-latlng_fail';
    s.geo.E_ADDR_START = 's-geo-addr_start';
    s.geo.E_ADDR_DONE = 's-geo-addr_done';
    s.geo.E_ADDR_FAIL = 's-geo-addr_fail';
    
    s.geo.def_options = {
        'enableHighAccuracy': true,
        'maximumAge': 0
    }
    
    s.geo.j_addrbar = false;
    
    // due with lattidue and longitude that more than 7 float point
    // e.g. safari has 8        
    s.geo.trunk_latlng = function(str){
        var str = str.toString(),
            pidx = str.indexOf('.');
            
        if(-1 === pidx){
            return str;
        } else {
            return str.substr(0, pidx+8);    
        }
    }
    
    s.geo.get_location = function(options){
        if(navigator.geolocation) {            
            s.j_doc.trigger(s.geo.E_LATLNG_START);
          
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = s.geo.trunk_latlng(position.coords.latitude),
                    lng = s.geo.trunk_latlng(position.coords.longitude);
                
                $.when(function(){
                    try {
                        return position.address.street + ' ' + 
                            position.address.streetNumber;
                    } catch (e) {
                        s.j_doc.trigger(s.geo.E_ADDR_START);
                        return $.ajax(LATLNG_TO_ADDR_API, {
                            data: {
                                'lat': lat,
                                'lng': lng
                            },
                            dataType: 'text'});
                    }
                }).
                done(function(addr){
                    s.j_doc.trigger(s.geo.E_ADDR_DONE);
                    s.j_doc.trigger(s.geo.E_LATLNG_DONE, [lat, lng, addr]);
                }). 
                fail(function(){
                    s.j_doc.trigger(s.geo.E_ADDR_FAIL);
                });
            }, 
            function() {
                s.j_doc.trigger(s.geo.E_LATLNG_FAIL);
            }, 
            $.extend({}, s.geo.def_options, options));
        } else {
            s.j_doc.trigger(s.geo.E_NOT_SUPPORT);
        }
    };
    
    s.geo.latlng2addr = function(lat, lng, callback){
        var settings = {
            data: {
                'lat': lat,
                'lng': lng
            },
            dataType: 'text'
        }
        
        if('function' === typeof callback){
            settings.success = callback;
        }
        
        return $.ajax(LATLNG_TO_ADDR_API, settings);
    };
    
    s.geo.update_locbar_start = function(j_locbar, message){
        j_locbar.removeClass('done fail').addClass('ing');
        j_locbar.find('.stat').text(LOCATING_MSG);
    }
    
    s.geo.update_locbar = function(j_locbar, lat, lng, addr){
        j_locbar.removeClass('ing').addClass('done');
        j_locbar.find('.lat').text(lat);
        j_locbar.find('.lng').text(lng);
        j_locbar.find('.addr').text(addr);
        j_locbar.find('.stat').empty();
    };
    
    s.geo.update_locbar_err = function(j_locbar, message){
        j_locbar.removeClass('ing').addClass('fail');
        j_locbar.find('.stat').text(message);
    }
    
    function update_locuri(uri, lat, lng, addr){
        var ar = uri.split('?'),
            path = ar[0];
            
        try {
            params = $.deparam(ar[1]);
        } catch (e) {
            params = {};
        }
            
        params.lat = lat;
        params.lng = lng;
        params.addr = addr;
        
        return path + '?' + $.param(params);
    }
    
    s.geo.update_loclink = function(j_loclink, lat, lng, addr){
        j_loclink.each(function(idx, el){
            var j_t = $(el);
            j_t.attr('href', update_locuri(j_t.attr('href'), lat, lng, addr));
        });
    };
    
    s.geo.update_locform = function(j_locform, lat, lng, addr){
        j_locform.each(function(idx, el){
            var j_t = $(el);
            j_t.find('[name=lat]').val(lat);
            j_t.find('[name=lng]').val(lng);
            j_t.find('[name=addr]').val(addr);
        });
    };
    
    function log(e){
        console.log(e.type);
    }
    
    function init_locbar(j_locbar){
        s.j_doc.bind(s.geo.E_LATLNG_START, function(e){
            s.geo.update_locbar_start(j_locbar, LOCATING_MSG);
        }).
        bind(s.geo.E_ADDR_START, function(e){
            s.geo.update_locbar_start(j_locbar, ADDRESSING_MSG);
        })
        .bind(s.geo.E_LATLNG_DONE, function(e, lat, lng, addr){
            s.geo.update_locbar(j_locbar, lat, lng, addr)
        }).
        bind(s.geo.E_LATLNG_FAIL, function(e){
            s.geo.update_locbar_err(j_locbar, FAILED_LOCATION_MSG);
        }).
        bind(s.geo.E_ADDR_FAIL, function(e){
            s.geo.update_locbar_err(j_locbar, FAILED_ADDRESSING_MSG);
        });
    }
    
    function init_loclink(j_loclink){
        s.j_doc.bind(s.geo.E_LATLNG_DONE, function(e, lat, lng, addr){
            s.geo.update_loclink(j_loclink, lat, lng, addr)
        });
    }
    
    function init_locform(j_locform){
        s.j_doc.bind(s.geo.E_LATLNG_DONE, function(e, lat, lng, addr){
            s.geo.update_locform(j_locform, lat, lng, addr)
        });
    }
    
    function start(options){
        var lat = s.geo.j_locbar.find('.lat').text().trim(),
            lng = s.geo.j_locbar.find('.lng').text().trim(),
            addr = s.geo.j_locbar.find('.addr').text().trim();
            
        if(lat && lng && addr){
            s.j_doc.trigger(s.geo.E_LATLNG_DONE, [lat, lng, addr]);
        } else {
            s.geo.get_location(options);
        }
    }
    
    s.geo.init = function(callback, options){
        s.geo.j_locbar = $('.locbar');
        s.geo.j_loclink = $('.loclink');
        s.geo.j_locform = $('.locform');
            
        console && s.j_doc.bind(s.geo.E_NOT_SUPPORT, log).
            bind(s.geo.E_LATLNG_START, log).
            bind(s.geo.E_LATLNG_DONE, log).
            bind(s.geo.E_LATLNG_FAIL, log).
            bind(s.geo.E_ADDR_START, log).
            bind(s.geo.E_ADDR_DONE, log).
            bind(s.geo.E_ADDR_FAIL, log);
            
        s.geo.j_locbar && init_locbar(s.geo.j_locbar);
        s.geo.j_loclink && init_loclink(s.geo.j_loclink);
        s.geo.j_locform && init_locform(s.geo.j_locform);
            
        if('function' === typeof callback){
            callback();
        } else if('object' === typeof callback){
            options = callback;
        }
            
        start(options);    
    };
})(jQuery);

jQuery(function($){
    // hide address bar on android built-in browser
    s.j_doc.scrollTop(1);
    s.j_doc.scrollTop(0);
    
    $('form').each(function(idx, el){
        var j_form = $(el);
        j_form.find('[type=text],[type=password], textarea').
            width(j_form.width()-10);
    });
});
