jQuery.noConflict();

(function($)
{
	window.eva = {
		/*  */

		/* common element */
		container : false,
		api : false,
		tpl : {},
		debug : true,
		conditionLs : [],
		exampleUid : 10007,
		conditionQueue : [],

		/* */

		buildMarkup : function()
		{
			if(!eva.api)
			{
				throw 'api data not loaded';
			}

			$.each(eva.api.entries, function(entityName,entity)
			{
				var $entity = eva.tpl.entity.clone().appendTo('#eva-main');
				$entity.find('.eva-entityName').text(entityName);
				var $entityBody = $entity.find('.bd');

				$.each(entity, function(methodName,method)
				{
					method.url = eva.api.baseUri + '/' + entityName + '/' + methodName + '/';

					var $method = eva.tpl.method.clone().appendTo($entityBody);
					$method.find('.eva-methodName').text(methodName);
					var $methodBody = $method.find('.bd');

					var baseAjaxCfg = {
						url: eva.apiBaseUri + method.path,
						type: method.type,
						dataType: 'json'
					};

					$.each(method.conditions, function(i,condition)
					{
						condition.method = method;
						eva.conditionLs.push(condition);
						condition.id = 'eva-condition-' + (eva.conditionLs.length - 1);

						var $condition = eva.tpl.condition.clone().attr('id',condition.id);

						$condition.find('.eva-status').addClass('eva-available');

						var summary;

						if( condition.desc )
						{
							summary = condition.desc;
						}
						else
						{
							summary = condition.params.toSource();
							summary = summary.substr(2,summary.length-4);
						}

						$condition.find('.eva-desc').text(summary);

						var $params = $condition.find('.eva-params');

						$.each(condition.params, function(key, value)
						{
							eva.tpl.param.clone().
								find('.eva-key').text(key).
								end().find('.eva-value').text( eva.printJSON(value) ).
								end().appendTo($params);
						});

						$methodBody.append($condition);
						eva.collapseCondition($condition,true);
					});

					eva.collapseMethod($method,true);
				});

				eva.collapseEntity($entity,true);
			});
		},

		queueCondition : function($conditions)
		{
			if(!$conditions.hasClass('eva-condition'))
			{
				$conditions = $conditions.find('.eva-condition');
			}

			eva.conditionQueue = $conditions.find('.eva-status').removeClass('eva-success eva-error').addClass('eva-queued').text('queued').
				end().get();

			eva.runQueue();
		},

		runQueue : function()
		{
			if(eva.conditionQueue.length)
			{
				eva.runCondition($(eva.conditionQueue.shift()));
			}
		},

		runCondition : function($condition)
		{
			var condition = false;

			try{
				var conditionIndex = parseInt($condition.attr('id').split('-')[2],10);
				condition = eva.conditionLs[conditionIndex];
			}
			catch(e)
			{
				return;
			}

			var start, end, statusClass, statusText, responseHtml;
			start = (new Date()).getTime();
			
			var data = condition.params;
			if('POST' === condition.method.type){
			    data.csrfmiddlewaretoken = pyrcp.get_csrf();
			}

			$.ajax({
				url: condition.method.url,
				type: condition.method.type,
				dataType: 'json',
				data: data,
				beforeSend: function(xhr, settings)
				{
					$condition.find('.eva-status').removeClass('eva-queued').addClass('eva-ing').text('&nbsp;');
					xhr.setRequestHeader('uid',eva.exampleUid);
				},
				success: function(data, textStatus, xhr)
				{
					end = (new Date()).getTime();

					try{
						if(!data)
						{
							throw 'empty response';
						}

						if( 'function' === typeof condition.validator )
						{
							condition.validator(data);
						}
						else if( parseInt(data.errorCode) )
						{
							throw data.sysMsg;
						}

						statusClass = 'eva-success';
						statusText = data.sysMsg ? data.sysMsg : xhr.statusText;
					}
					catch(error)
					{
						statusClass = 'eva-error';
						statusText = error;
					}

					responseHtml = data ? '<pre>'+ eva.printJSON($.parseJSON(xhr.responseText)) +'</pre>' : '';
				},
				error: function(xhr, httpStatusText, errorThrown)
				{
					end = (new Date()).getTime();
					statusClass = 'eva-error';
					statusText = xhr.statusText + ' / ' + httpStatusText;

					if('parsererror' === httpStatusText)
					{
						responseHtml = xhr.responseText;
					}
					else
					{
						responseHtml = '&nbsp;';
					}
				},
				complete : function (xhr, textStatus)
				{
					duration = end - start;

					$condition.addClass(statusClass).find('.eva-ing').removeClass('eva-ing').
						end().find('.eva-status').text( '[ ' + duration + ' ms ] ' + xhr.status + ' : ' + statusText ).
						end().find('.eva-response').html( responseHtml );

					eva.runQueue();
				}
			});
		},

		expandEntity : function($entity)
		{
			$entity.removeClass('eva-collapsed').addClass('eva-expanded').
				find('.eva-entityName').prev('.eva-indicator').text('-').
				end().end().find('.eva-methodLs').slideDown('fast');
		},

		collapseEntity : function($entity, noAnim)
		{
			$entity.removeClass('eva-expanded').addClass('eva-collapsed').
				find('.eva-entityName').prev('.eva-indicator').text('+');

			if(noAnim)
			{
				$entity.find('.eva-methodLs').hide();
			}
			else
			{
				$entity.find('.eva-methodLs').slideUp('fast');
			}
		},

		expandMethod : function($method)
		{
			$method.removeClass('eva-collapsed').addClass('eva-expanded').
				find('.eva-methodName').prev('.eva-indicator').text('-').
				end().end().find('.eva-conditionLs').slideDown('fast');
		},

		collapseMethod : function($method, noAnim)
		{
			$method.removeClass('eva-expanded').addClass('eva-collapsed').
				find('.eva-methodName').prev('.eva-indicator').text('+');

			if(noAnim)
			{
				$method.find('.eva-conditionLs').hide();
			}
			else
			{
				$method.find('.eva-conditionLs').slideUp('fast');
			}
		},

		expandCondition : function($condition)
		{
			$condition.removeClass('eva-collapsed').addClass('eva-expanded').
				find('.eva-extra').slideDown('fast');
		},

		collapseCondition : function($condition, noAnim)
		{
			$condition.removeClass('eva-expanded').addClass('eva-collapsed');

			if(noAnim)
			{
				$condition.find('.eva-extra').hide();
			}
			else
			{
				$condition.find('.eva-extra').slideUp('fast');
			}
		},

		printJSON : function (obj, depth)
		{
			var output = '';
			var lastComma;

			if( 'undefined' === typeof depth ) { depth=0; }

			if($.isArray(obj))
			{
				output = "[\n";

				$.each(obj ,function(i ,ele)
				{
					output += eva.printJSON(ele, ++depth) + ', ';
				});

				lastComma = output.length-2

				if( ',' === output[lastComma])
				{
					output = output.substr(0,lastComma) + "\n";
				}

				output += "]\n";
			}
			else if( 'object' === typeof obj )
			{
				output = "{\n";

				$.each(obj, function(key, value)
				{
					if( 'object' === typeof value )
					{
						$.each(obj, function(key, value)
						{
							output += eva.printJSON(value, ++depth);
						});
					}
					else
					{
						for(i=0;i<=depth;i++)
						{
							output += "  ";
						}
						output += ( key + ' : ' + value + ",\n" );
					}
				});

				lastComma = output.length-2

				if( ',' === output[lastComma])
				{
					output = output.substr(0,lastComma) + "\n";
				}

				output += "}\n";
			}
			else
			{
				output = obj;
			}

			return output;
		}
	};

	$(function(){

		eva.container = $('#eva-container');
		eva.container.find('.eva-tpl').each(function(i,e)
		{
			var _tpl = $(this).removeClass('eva-tpl').removeClass('s-h').remove();
			eva.tpl[_tpl.attr('tplName')] = _tpl;
			_tpl.removeAttr('tplName');
		});

		eva.container.delegate('.eva-toggleEntity', 'click', function(e)
		{
			e.preventDefault();
			var _entity = $(e.target).closest('.eva-entity');
			if( _entity.length )
			{
				if(_entity.hasClass('eva-collapsed'))
				{
					eva.expandEntity(_entity);
				}
				else
				{
					eva.collapseEntity(_entity);
				}
			}
		}).
		delegate('.eva-toggleMethod', 'click', function(e)
		{
			e.preventDefault();
			var _method = $(e.target).closest('.eva-method');
			if( _method.length )
			{
				if(_method.hasClass('eva-collapsed'))
				{
					eva.expandMethod(_method);
				}
				else
				{
					eva.collapseMethod(_method);
				}
			}
		}).
		delegate('.eva-toggleCondition', 'click', function(e)
		{
			e.preventDefault();
			var _condition = $(e.target).closest('.eva-condition');
			if( _condition.length )
			{
				if(_condition.hasClass('eva-collapsed'))
				{
					eva.expandCondition(_condition);
				}
				else
				{
					eva.collapseCondition(_condition);
				}
			}
		}).
		delegate('.eva-run', 'click', function(e)
		{
			e.preventDefault();
			var _$t = $(e.target);
			if( _$t.hasClass('eva-run-entity') )
			{
				var _$entity = _$t.closest('.eva-entity');
				eva.expandEntity(_$entity);
				_$entity.find('.eva-method').each(function(i, ele)
				{
					var _$method = $(ele);
					eva.expandMethod(_$method);
				});
				eva.queueCondition(_$entity);
			}
			else if( _$t.hasClass('eva-run-method') )
			{
				var _$method = _$t.closest('.eva-method');
				eva.expandMethod(_$method);
				eva.queueCondition(_$method);
			}
			else
			{
				var _$condition = _$t.closest('.eva-condition');
				eva.expandCondition(_$condition);
				eva.queueCondition(_$condition);
			}
		});

		// replace attributes when url param "d" exists with any value
		if(/[?&]d[=&]|\?d$|\&d$/.test(location.search))
		{
			eva.debug = true;
			eva.api.baseUri = 'pseudoApi';

			$.each(eva.api.entries, function(entryName, entry)
			{
				$.each(entry, function(methodName, method)
				{
					method.type = 'GET';
				});
			});
		}

		eva.buildMarkup();
	});

})(jQuery);
