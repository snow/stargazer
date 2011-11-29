(function($)
{
	if( 'undefined' === typeof window.eva.api ) { return; }

	window.eva.api = {
		baseUri : 'http://eva.fe/pseudoApi',
		entries : {
			account : {
				signup : {
					type : 'POST',
					conditions : [
						{
							desc : 'success or duplicate',
							params : {
								username : 'snowhs',
								email : 'snow@firebloom.cc',
								password : 'asdfgh'
							},
							validator : function(data)
							{
								if( 0 > $.inArray( parseInt(data.errorCode, 10), [0, 4] ) )
								{
									throw data.sysMsg;
								}
							}
						},
						{
							desc : 'missing username',
							params : {
								username : '',
								email : 'snow@firebloom.cc',
								password : 'asdfgh'
							},
							validator : function(data)
							{
								if( parseInt(data.errorCode, 10) !== 5 )
								{
									throw data.sysMsg;
								}
							}
						},
						{
							desc : 'missing email',
							params : {
								username : 'snowhs',
								email : '',
								password : 'asdfgh'
							},
							validator : function(data)
							{
								if( parseInt(data.errorCode, 10) !== 3 )
								{
									throw data.sysMsg;
								}
							}
						},
						{
							desc : 'missing password',
							params : {
								username : 'snowhs',
								email : 'snow@firebloom.cc',
								password : ''
							},
							validator : function(data)
							{
								if( parseInt(data.errorCode, 10) !== 2 )
								{
									throw data.sysMsg;
								}
							}
						},
						{
							desc : 'missing email and password',
							params : {
								username : 'snowhs',
								email : '',
								password : ''
							},
							validator : function(data)
							{
								if( 0 > $.inArray( parseInt(data.errorCode, 10), [2, 3] ) )
								{
									throw data.sysMsg;
								}
							}

						},
						{
							desc : 'invalid username',
							params : {
								username : 'snow.%^hs',
								email : 'snow@firebloom.cc',
								password : 'asdfgh'
							}
						},
						{
							desc : 'invalid email',
							params : {
								username : 'snowhs',
								email : 'snowreblooc',
								password : 'asdfgh'
							}
						},
						{
							desc : 'invalid password',
							params : {
								username : 'snowhs',
								email : 'snow@firebloom.cc',
								password : 'as'
							}
						}
					]
				},
				signin : {
					type : 'POST',
					conditions : [
						{
							desc : 'default',
							params : {
								username : 'snowhs',
								password : 'asdfgh'
							}
						},
						{
							desc : 'missing username',
							params : {
								username : '',
								password : 'asdfgh'
							},
							validator : function(data)
							{
								if( parseInt(data.errorCode, 10) !== 5 )
								{
									throw data.sysMsg;
								}
							}
						},
						{
							desc : 'missing password',
							params : {
								username : 'snowhs',
								password : ''
							},
							validator : function(data)
							{
								if( parseInt(data.errorCode, 10) !== 2 )
								{
									throw data.sysMsg;
								}
							}
						},
						{
							desc : 'didn\'t signed up',
							params : {
								username : 'snowhssss',
								password : 'asdfgh'
							},
							validator : function(data)
							{
								if( parseInt(data.errorCode, 10) !== 1 )
								{
									throw data.sysMsg;
								}
							}
						}
					]
				}
			}
		}
	};
})(jQuery);
