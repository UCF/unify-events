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


//$('#repeat-dialog').dialog({ modal  : true });
$('.buttons').buttonset();


$('.when-where').each(function(){
	//date
	$(this).find('.date').datepicker();

	//time
	var end = $(this).find('.end');
	var add = $(this).find('.add.end-time').click(function(){
		$(this).hide();
		end.show();
	});
	$(this).find('.remove.rm-time').click(function(){
		add.show()
		end.hide();
	});

	//location
	var st = $(this).find('.street');
	var pl = $(this).find('.place');
	var swap = $(this).find('.add.address,.remove.rm-addr');
	swap.click(function(){
		pl.toggle();
		st.toggle();
		swap.show();
		$(this).hide();
	});

	//recurrence
	$(this).find('.rec').click(function(){
		return;
	});
});







/* for the old form, can be removed later */
$().ready(function() {
	$('#event_instance_add')
		.click(function() {
			extend_formset('#instances > li:last', 'event_instance');
			return false;
		});
});
