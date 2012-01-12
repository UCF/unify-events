$('#title input')
	.keyup(function(){
		var el= $(this);
		if(el.val().length > 64) {
			el.addClass('error');
			$('#title div.label').hide();
			$('#title div.error').show();
		} else {
			el.removeClass('error');
			$('#title div.label').show();
			$('#title div.error').hide();
		}
	})
	.blur(function(){
		var len = $(this).val().length;
		if(len>0 && len<64){
			$('#title h3 span').addClass('check');
		} else {
			$('#title h3 span').removeClass('check');
		}
	});





/* for the old form, can be removed later */
$().ready(function() {
	$('#event_instance_add')
		.click(function() {
			extend_formset('#instances > li:last', 'event_instance');
			return false;
		});
});
