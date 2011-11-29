(function($)
{
	if( 'undefined' === typeof window.eva ) { return; }
	
	window.eva.api = {
	    baseUri: '/api',
	    entries: {
	        utils: {},
	        posts: {},
	        users: {},
	        accounts: {}
	    }
	};
	
	eva.api.entries.utils.latlng2addr = {
	    type: 'POST',
	    conditions: [
	       {
	           desc: 'success',
	           params: {
	               lat: 30,
	               lng: 101
	           },
	           validator: function(data){
	               return true;
	           }
	       }
	    ]
	};
})(jQuery);
