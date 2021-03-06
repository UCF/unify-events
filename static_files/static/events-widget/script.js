/*
	EVENTS CALENDAR WIDGETS
	UCF Web Communcations
	Summer 2010
*/

(function($) {
	$.getUCFEvents = function(options, callback){
		var settings = $.extend({
			'url'         : 'https://events.ucf.edu',
			'calendar_id' : 1,
			'limit'       : 4
		}, options);

		var data = {
			'format'      : 'json',
			'upcoming'    : 'upcoming',
			'calendar_id' : settings.calendar_id,
			'limit'       : settings.limit
		};

		$.ajax({
			dataType : 'json',
			url      : settings.url,
			data     : data,
			success  : callback,
			error    : function(request, status, error){
				callback(new Array(), status, request);
			}
		});
	};

	$.fn.eventsUCF = function() {
		// all values are optional
		var defaults = {
			'url'          : 'https://events.ucf.edu',
			'limit'        : 4,
			'calendar_id'  : 1,
			'monthwidget'  : false,
			'month'        : false,
			'year'         : false
		};

		this.each(function() {
			// pull options from data attribute
			var cal = $(this);
			var options = {
				'url'          : cal.attr('data-url'),
				'limit'        : cal.attr('data-limit'),
				'calendar_id'  : cal.attr('data-calendar-id'),
				'monthwidget'  : cal.attr('data-monthwidget'),
				'month'        : cal.attr('data-month'),
				'year'         : cal.attr('data-year')
			};

			var settings = $.extend({}, defaults, options);
			var url      = settings.url;

			// set the ajax data / query string according to options
			var data = {
				'is_widget'   : true,
				'calendar_id' : settings['calendar_id'],
				'limit'       : settings['limit']
			};

			if(settings.monthwidget){
				data.monthwidget = true;
			}
			if(settings.year || settings.month){
				var d  = new Date();
				data.year = (settings.year) ? settings.year : d.getFullYear();
				data.month = (settings.month) ? settings.month : d.getMonth() + 1;
			}

			var Browser = {
			  Version: function() {
			    var version = 999; // we assume a sane browser
			    if (navigator.appVersion.indexOf("MSIE") != -1)
			      // bah, IE again, lets downgrade version number
			      version = parseFloat(navigator.appVersion.split("MSIE")[1]);
			    return version;
			  }
			};

			var showFallbackMsg = function(){
				// Old IE always gets a link to the upcoming view
				var qstring = 'calendar_id='+ data.calendar_id + '&upcoming=upcoming';
				url = url + '?' + qstring;
				msg = '<a href="'+ url +'">View Calendar</a>';
				cal.html(msg);
			};

			// check for IE7
			var sadtimes = false;
			if (navigator.appVersion.indexOf("MSIE") != -1){
				var version = parseFloat(navigator.appVersion.split("MSIE")[1]);
				if(version<8) sadtimes = true;
			}

			if(sadtimes) {
				showFallbackMsg();
			} else {
				try {
					$.ajax({
					  url: url,
					  data: data,
					  success: function(html){cal.html(html);} // cannot use .parseHTML here--not supported until jquery v1.8
					});
				} catch(e){
					showFallbackMsg();
				}
			}
		});

		return this;

	};
})(jQuery);
