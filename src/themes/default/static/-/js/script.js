var sluggify = function(s) {return s.toLowerCase().replace(/\s/g, '-').replace(/[^A-Za-z-]/, '');}

var Webcom = {};

Webcom.calendarWidget = function($){
	$('.calendar-widget .month-controls a').click(function(){
 		var url    = $(this).attr('href');
		var parent = $(this).parents('.calendar-widget');
		$.ajax(url, {
			'success' : function(data){
				parent.fadeOut(400, function(){
					var replace = $(data);
					replace.hide();
					parent.replaceWith(replace);
					replace.fadeIn(400);
					Webcom.calendarWidget($);
				});
			}
		});
		return false;
	});
};

$().ready(function(){
	Webcom.calendarWidget(jQuery);
	
	// EventInstance DatePickers
	$('.datepicker').datepicker();

	// Other Actions Nav Dropdown
	$('#other_actions li:gt(0)')
		.css('visibility','hidden')
	$('#other_actions li')
		.hover(
			function() {
				$('#other_actions li:gt(0)').css('visibility', 'visible')
			},
			function() {
				$('#other_actions li:gt(0)').css('visibility', 'hidden')
			}
		);
});