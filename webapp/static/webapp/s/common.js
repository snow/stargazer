/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.sgz = {}
})(jQuery);

/*
 * tools for stream
 * ------------------
 */
(function($) {
    sgz.stream = {}

    sgz.stream.init = function(j_stream, params){
        var uri = '/api/posts/';
        if(params.lat && params.lng){
            uri += 'lat'+params.lat+'/lng'+params.lng+'/'+params.type+'.html';
            delete params.lat;
            delete params.lng;
        } else if(params.id){
            uri += 'by/' + params.id + '.html';
            delete params.id
        }
        
        j_stream.attr('content_uri', uri);
        sgz.stream.load(j_stream, params);
        
        j_stream.delegate('.stream-item .ban', 'click', function() {
            sgz.stream.ban(this);
        }).delegate('.stream-item .like', 'click', function() {
            sgz.stream.like(this);
        });
    };

    sgz.stream.load = function(j_stream, params){
        $.ajax(j_stream.attr('content_uri'), {
            'type': 'GET',
            'data': params,
            'success': function(data){
                j_stream.append(data);
            }
        });
    };

    sgz.stream.ban = function(anchor) {
        var j_stream_item = $(anchor).closest('.stream-item'),
            id = j_stream_item.attr('sid');

        return pyrcp.post('/api/posts/ban/'+id+'/', {
            'success': function(data){
                j_stream_item.hide('fast', function() {
                    $(this).remove();
                });
            },
            'dataType': 'json'
        });
    };

    sgz.stream.like = function(anchor) {
        var j_anchor = $(anchor),
            cur_like_cnt = parseInt(j_anchor.text()),
            j_stream_item = j_anchor.closest('.stream-item'),
            id = j_stream_item.attr('sid');

        if('NaN' === cur_like_cnt.toString())
        {
            cur_like_cnt = 0;
        }

        return pyrcp.post('/api/posts/like/'+id+'/', {
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

        LATLNG_TO_ADDR_API = '/api/utils/ll2a/';

    sgz.geo = {
        initialized: false,
        lat: false,
        lng: false,
        addr: FALLBACK_ADDR
    };

    /*sgz.geo.initialized = false;
    sgz.geo.lat = false;
    sgz.geo.lng = false;
    sgz.geo.addr = false;*/

    sgz.geo.E_NOT_SUPPORT = 's-geo-not_support';
    sgz.geo.E_LATLNG_START = 's-geo-latlng_start';
    sgz.geo.E_LATLNG_DONE = 's-geo-latlng_done';
    sgz.geo.E_LATLNG_FAIL = 's-geo-latlng_fail';
    sgz.geo.E_ADDR_START = 's-geo-addr_start';
    sgz.geo.E_ADDR_DONE = 's-geo-addr_done';
    sgz.geo.E_ADDR_FAIL = 's-geo-addr_fail';

    sgz.geo.def_options = {
        'enableHighAccuracy': true,
        'maximumAge': 30 * 60 * 1000 // 30min
    };

    sgz.geo.C_LOCBAR = 'locbar';
    sgz.geo.S_LOCBAR = '.' + sgz.geo.C_LOCBAR;
    sgz.geo.C_LOCLINK = 'loclink';
    sgz.geo.S_LOCLINK = '.' + sgz.geo.C_LOCLINK;
    sgz.geo.C_LOCFORM = 'locform';
    sgz.geo.S_LOCFORM = '.' + sgz.geo.C_LOCFORM;

    // round lattidue or longitude to given decimal point
    // defaults to 7
    // e.g. safari has 8
    sgz.geo.trunk_latlng = function(value, accuracy){
        if('undefined' === typeof accuracy){
            accuracy = 7;
        }
        
        var value = parseFloat(value),
            i = Math.pow(10, accuracy);

        return Math.round(value * i) / i;
    };
    
    // recieve address in callback function by given latlng
    sgz.geo.latlng2addr = function(lat, lng, success, error){
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

        return pyrcp.post(LATLNG_TO_ADDR_API, params);
    };
    
    sgz.geo.update_locuri = function(uri, lat, lng, addr){
        var latregx = /lat\d+\.?\d*/i,
            lngregx = /lng\d+\.?\d*/i,
            nearbyregx = /\/nearby\//i;
            
        lat = sgz.geo.trunk_latlng(lat, 5);
        lng = sgz.geo.trunk_latlng(lng, 5);
        
        if(-1 < uri.search(nearbyregx)){
            return uri.replace(nearbyregx, '/lat'+lat+'/lng'+lng+'/');
        } else if(-1 < uri.search(latregx) && -1 < uri.search(lngregx)){
            return uri.replace(latregx, 'lat'+lat).replace(lngregx, 'lng'+lng);
        } else {
            var ar = uri.split('?'),
                path = ar[0];
    
            try {
                params = $.deparam(ar[1]);
                params.lat && (params.lat = lat);
                params.lng && (params.lng = lng);
                params.addr && (params.addr = addr);
            } catch (e) {
                params = {};
            }
    
            return path + '?' + $.param(params);
        }
    };
    
    function get_address(lat, lng){
        var addr = FALLBACK_ADDR;
        
        $.when(sgz.geo.latlng2addr(lat, lng)).
        done(function(data){
            pyrcp.j_doc.trigger(sgz.geo.E_ADDR_DONE);
            addr = data.addr;
        }).
        fail(function(){
            pyrcp.j_doc.trigger(sgz.geo.E_ADDR_FAIL);
        }).
        then(function(){
            pyrcp.j_doc.trigger(sgz.geo.E_LATLNG_DONE, [lat, lng, addr]);
        });
    }

    function get_location(options){
        if(navigator.geolocation) {
            pyrcp.j_doc.trigger(sgz.geo.E_LATLNG_START);

            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = sgz.geo.trunk_latlng(position.coords.latitude),
                    lng = sgz.geo.trunk_latlng(position.coords.longitude);

                if(position.address){
                    pyrcp.j_doc.trigger(sgz.geo.E_LATLNG_DONE,
                        [lat, lng, position.address.street + ' ' +
                            position.address.streetNumber]);
                } else {
                    pyrcp.j_doc.trigger(sgz.geo.E_ADDR_START, [lat, lng]);
                }
            },
            function() {
                pyrcp.j_doc.trigger(sgz.geo.E_LATLNG_FAIL);
            },
            $.extend({}, sgz.geo.def_options, options));
        } else {
            pyrcp.j_doc.trigger(sgz.geo.E_NOT_SUPPORT);
        }
    };
    
    function locbar_on_start(evt){
        var j_locbar = $(sgz.geo.S_LOCBAR),
            msg;
            
        j_locbar.removeClass('done fail').addClass('ing');
        
        if(sgz.geo.E_LATLNG_START === evt.type){
            msg = LOCATING_MSG;
        } else {
            msg = ADDRESSING_MSG;
        }
        j_locbar.find('.stat').text(msg);
        
        j_locbar.find('.addr').empty();
    }
    
    function locbar_on_fail(evt){
        var j_locbar = $(sgz.geo.S_LOCBAR);
        j_locbar.removeClass('ing').addClass('fail');
        
        if(sgz.geo.E_LATLNG_FAIL === evt.type){
            msg = FAILED_LOCATION_MSG;
        } else if(sgz.geo.E_ADDR_FAIL === evt.type){
            msg = FAILED_ADDRESSING_MSG;
        } else {
            msg = NO_GEO_MSG;
        }
        j_locbar.find('.stat').text(msg);
    }
    
    function on_addr_start(evt, lat, lng){
        get_address(lat, lng);
        locbar_on_start(evt);
    }
    
    function on_latlng_done(evt, lat, lng, addr){
        sgz.geo.lat = lat;
        sgz.geo.lng = lng;
        sgz.geo.addr = addr;
        sgz.geo.initialized = true;
        
        var j_locbar = $(sgz.geo.S_LOCBAR);
        j_locbar.removeClass('ing').addClass('done');
        j_locbar.find('.lat').text(lat);
        j_locbar.find('.lng').text(lng);
        j_locbar.find('.addr').text(addr);
        j_locbar.find('.stat').empty();
        
        $(sgz.geo.S_LOCLINK).each(function(idx, el){
            var j_t = $(el);
            j_t.attr('href', sgz.geo.update_locuri(j_t.attr('href'), 
                                                   lat, lng, addr));
        });
        
        $(sgz.geo.S_LOCFORM).each(function(idx, el){
            var j_t = $(el);
            j_t.find('[name=latitude]').val(lat);
            j_t.find('[name=longitude]').val(lng);
            j_t.find('[name=address]').val(addr);
        });
    }

    function init(){
        console && pyrcp.j_doc.bind(
            [
                sgz.geo.E_NOT_SUPPORT, 
                sgz.geo.E_LATLNG_START, 
                sgz.geo.E_LATLNG_DONE,
                sgz.geo.E_LATLNG_FAIL,
                sgz.geo.E_ADDR_START,
                sgz.geo.E_ADDR_DONE,
                sgz.geo.E_ADDR_FAIL
            ].join(' '), 
            function(evt){
                console.log(evt.type);
            }
        );
        
        evtmap = {}
        
        evtmap[sgz.geo.E_LATLNG_START] = locbar_on_start;
        evtmap[sgz.geo.E_LATLNG_DONE] = on_latlng_done;
        
        evtmap[sgz.geo.E_ADDR_START] = on_addr_start;
        
        evtmap[sgz.geo.E_NOT_SUPPORT] = locbar_on_fail;
        evtmap[sgz.geo.E_LATLNG_FAIL] = locbar_on_fail;        
        evtmap[sgz.geo.E_ADDR_FAIL] = locbar_on_fail;
        
        pyrcp.j_doc.bind(evtmap);
    }
    
    init();

    sgz.geo.start = function(options){
        if(sgz.geo.initialized){
            pyrcp.j_doc.trigger(sgz.geo.E_LATLNG_DONE, 
                                [sgz.geo.lat, 
                                 sgz.geo.lng, 
                                 sgz.geo.addr]);
                                 
        } else if(sgz.geo.lat && sgz.geo.lng){
            pyrcp.j_doc.trigger(sgz.geo.E_ADDR_START, 
                                [sgz.geo.lat, sgz.geo.lng]);
        } else {
            get_location(options);
        }
    };
})(jQuery);
/**
 * form helpers
 * -----------------------------
 */
(function($){
    sgz.forms = {};
    
    sgz.forms.S_TEXT = '[type=text],[type=password]';
    
    sgz.forms.init = function(j_form){
        j_form.find(sgz.forms.S_TEXT).each(function(idx, el){
            var j_t = $(el);
            if('' === j_t.val()){
                j_t.addClass('virgin');
                if('password' !== j_t.attr('type')){
                    j_t.val(j_t.attr('placeholder'));
                }
            } else if(j_t.val() === j_t.attr('placeholder')){
                j_t.addClass('virgin');
            }
        });
        
        j_form.find('.virgin[type=text]').one('focus', function(evt){
            $(this).select();
        });
        
        j_form.find('.virgin').one('keyup', function(evt){
            $(this).removeClass('virgin');
        });
    };
    
    sgz.forms.custom_submit = function(j_form){
        j_form.submit(function(evt){
            evt.preventDefault();
            
            pyrcp.post(j_form.attr('action'), {
                data: j_form.serialize(),
                success: function(data){
                    if(data.go_to){
                        $.mobile.changePage(data.go_to);
                    } else {
                        // TODO: non-redirect situations?
                    }                    
                },
                error: function(jqXHR){
                    try{
                        data = $.parseJSON(jqXHR.responseText);
                        j_form.find('.errls').empty();
                        var errls;
                        $.each(data.errors, function(key, errors){
                            if('__all__' === key){
                                errls = $('.errls.nonfield');
                                if(0 === errls.length){
                                    errls = $('<ul class="errls nonfield"/>').
                                                            prependTo(j_form);
                                }
                            } else {
                                errls = j_form.find('.errls.'+key);
                                if(0 === errls.length){
                                    errls = $('<ul class="errls '+key+'" />').
                                        insertBefore(
                                            j_form.find('[name='+key+']'));
                                }
                            }        
                             
                            $.each(errors, function(idx, err){
                                errls.append('<li>'+err+'</li>');
                            });
                        });
                    } catch(err) {
                        //TODO what will extractly happen here?
                        console && console.log(err);
                    }
                }
            });
        });
    }
})(jQuery);
/**
 * handle login_required links
 * -----------------------------
 */
(function($){
    function do_login_required_link(evt){
        evt.preventDefault();
        var href = $(evt.currentTarget).attr('href');
        if(sgz.is_signedin){
            $.mobile.changePage(href);
        } else {
            $.mobile.changePage('/w/signin/?next='+href);
        }
    }
    
    pyrcp.j_doc.delegate('a.login_required[data-ajax=false]', 'click', 
                         do_login_required_link);
})(jQuery);

/**
 * log the entry page
 */
(function($){
    pyrcp.j_doc.one('pagecreate', function(evt){
        var j_firstpg = $(evt.target);
        $.each(j_firstpg.attr('class').split(' '), function(idx, el){
            if('pg-' === el.substr(0, 3)){
                sgz.entry_page = el;
            }
        });
    });
})(jQuery);



jQuery(function($){
    // hide address bar on mobile browser
    /*$(window).load(function(){
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
    });*/
});
