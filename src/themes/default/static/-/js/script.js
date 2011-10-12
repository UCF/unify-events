var sluggify = function(s) {return s.toLowerCase().replace(/\s/g, '-').replace(/[^A-Za-z-]/, '');}

$().ready(function() {
	
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