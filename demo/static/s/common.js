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
