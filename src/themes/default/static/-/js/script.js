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
	
	// Calendar Selector
	$('#calendar_selector')	
		.submit(function() {
			var form     = $(this);
			var selector = $(this).find('select');
			window.location.href = selector.val();
			return false;
		})
});