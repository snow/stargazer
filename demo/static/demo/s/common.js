/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.s = {}

    s.j_doc = $(document);
    
    s.post = function(url, params){
        params.type = 'POST';
        
        if('undefined' === typeof s.csrf){
            s.csrf = $('[name=csrfmiddlewaretoken]').val();
        }
        if('undefined' === typeof params.data){
            params.data = {}
        }        
        params.data.csrfmiddlewaretoken = s.csrf
        
        return $.ajax(url, params);
    }
})(jQuery);

/*
 * tools for stream
 * ------------------
 */
(function($) {

    s.stream = {}

    var j_stream,
        csrf;

    s.stream.init = function(type, params){
        csrf = $('[name=csrfmiddlewaretoken]').val();
        j_stream = $('#stream');

        j_stream.delegate('.stream-item .ban', 'click', function() {
            s.stream.ban(this);
        }).delegate('.stream-item .like', 'click', function() {
            s.stream.like(this);
        });

        var uri = '/post/load/'+type+'/';
        if(params.id){
            uri += params.id + '/';
            delete params.id
        }

        s.stream.load(uri, params);
    };

    s.stream.load = function(CONTENT_URI, params){
        $.ajax(CONTENT_URI, {
            'type': 'GET',
            'data': params,
            'success': function(data){
                j_stream.append(data);
            }
        });
    };

    s.stream.ban = function(anchor) {
        var j_stream_item = $(anchor).closest('.stream-item'),
            id = j_stream_item.attr('sid');

        return s.post('/post/ban/',{
            'data': {'id': id},
            'success': function(data){
                j_stream_item.hide('fast', function() {
                    $(this).remove();
                });
            },
            'dataType': 'json'
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

        return s.post('/post/like/', {
            'data': {'id': id},
            'success': function(data){
                if(j_stream_item.hasClass('on')) {
                    j_anchor.text(Math.max(0, cur_like_cnt-1));
                    j_stream_item.removeClass('on');
                } else {
                    j_anchor.text(cur_like_cnt+1);
                    j_stream_item.addClass('on');
                }
            },
            'dataType': 'json'
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
        FALLBACK_ADDR = '一个神秘的地方',

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
    
    function get_address(lat, lng){
        var addr = FALLBACK_ADDR;
        
        $.when(s.geo.latlng2addr(lat, lng, function(data){
            if (data.error){
                s.j_doc.trigger(s.geo.E_ADDR_FAIL);
            } else {
                s.j_doc.trigger(s.geo.E_ADDR_DONE);
                addr = data.addr
            }
        }, function(){
            s.j_doc.trigger(s.geo.E_ADDR_FAIL);
        })).done(function(){
            s.j_doc.trigger(s.geo.E_LATLNG_DONE, [lat, lng, addr]);
        });
    }

    function get_location(options){
        if(navigator.geolocation) {
            s.j_doc.trigger(s.geo.E_LATLNG_START);

            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = s.geo.trunk_latlng(position.coords.latitude),
                    lng = s.geo.trunk_latlng(position.coords.longitude);

                if(position.address){
                    s.j_doc.trigger(s.geo.E_LATLNG_DONE,
                        [lat, lng, position.address.street + ' ' +
                            position.address.streetNumber]);
                } else {
                    s.j_doc.trigger(s.geo.E_ADDR_START, [lat, lng]);
                }
            },
            function() {
                s.j_doc.trigger(s.geo.E_LATLNG_FAIL);
            },
            $.extend({}, s.geo.def_options, options));
        } else {
            s.j_doc.trigger(s.geo.E_NOT_SUPPORT);
        }
    };

    s.geo.latlng2addr = function(lat, lng, success, error){
        var params = {
            data: {
                'lat': lat,
                'lng': lng
            },
            dataType: 'json'
        }

        if('function' === typeof success){
            params.success = success;
        }
        
        if('function' === typeof error){
            params.error = error;
        }

        return s.post(LATLNG_TO_ADDR_API, params);
    };

    s.geo.update_locbar_start = function(j_locbar, message){
        j_locbar.removeClass('done fail').addClass('ing');
        j_locbar.find('.stat').text(message);
        j_locbar.find('.addr').empty();
    };

    s.geo.update_locbar_done = function(j_locbar, lat, lng, addr){
        j_locbar.removeClass('ing').addClass('done');
        j_locbar.find('.lat').text(lat);
        j_locbar.find('.lng').text(lng);
        j_locbar.find('.addr').text(addr);
        j_locbar.find('.stat').empty();
    };

    s.geo.update_locbar_err = function(j_locbar, message){
        j_locbar.removeClass('ing').addClass('fail');
        j_locbar.find('.stat').text(message);
    };

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
            j_t.find('[name=latitude]').val(lat);
            j_t.find('[name=longitude]').val(lng);
            j_t.find('[name=address]').val(addr);
        });
    };

    function log(e){
        console.log(e.type);
    }

    function init_locbar(j_locbar){
        s.j_doc.bind(s.geo.E_LATLNG_START, function(e){
            s.geo.update_locbar_start(j_locbar, LOCATING_MSG);
        }).
        bind(s.geo.E_ADDR_START, function(e, lat, lng){
            s.geo.update_locbar_start(j_locbar, ADDRESSING_MSG);
            get_address(lat, lng);
        })
        .bind(s.geo.E_LATLNG_DONE, function(e, lat, lng, addr){
            s.geo.update_locbar_done(j_locbar, lat, lng, addr)
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
            get_location(options);
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
    // hide address bar on mobile browser
    $(window).load(function(){
        setTimeout(function(){
            // not work on android builtin browser with (0, 1) first
            window.scrollTo(0, 1);
            window.scrollTo(0, 0);
        }, 100);
    });

    $('form').each(function(idx, el){
        var j_form = $(el);
        j_form.find('[type=text],[type=password], textarea').
            width(j_form.width()-10);
    });
});
