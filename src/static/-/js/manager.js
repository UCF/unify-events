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


$('.buttons').buttonset();
$('#dialog-date').datepicker({ dateFormat: 'mm/d/y'});

/******************************************************************************\
  Prompt user to define / edit an event's when-where recurrence
\******************************************************************************/
Unify.recurrence = function(ww){
	
	// parse the event's recurrence data
	var data = JSON.parse($('#recurrence').val());
	if(data){
		$(ww).data(data);
	} else {
		// parse data from event form and fill data with defaults
		var txt = $(ww).find('.date').val();
		var date = $.datepicker.parseDate('mm/dd/y', txt);
		var dayNames = ['Sun', 'Mon', 'Tues', 'Wed', 'Thu', 'Fri', 'Sat'];
		var day = dayNames[date.getDay()];
		var until = new Date();
		var six_mo = 1000*60*60*24*183;
		until.setTime(date.getTime() + six_mo);
		var summary = "Repeats every " + day + " until " + $.datepicker.formatDate('M d, yy', until);
		$(ww).data({
			'date'     : date,
			'interval' : {
				'repeats' : 'week',
				'every'   : { 'week' : [day], 'month': 'dayofweek' },
				'until'   : $.datepicker.formatDate('mm/dd/y', until)
			},
			'summary'  : summary
		});
	}

	// init recur dialog with data (repeats, repeats-on, ends, summary)
	$('#repeats-week, #repeats-month').hide();
	$('#repeats-' + $(ww).data('interval').repeats).show();
	$('#repeat-dialog input').removeAttr('checked').removeAttr('selected');
	$('#repeat-dialog label').removeClass('ui-state-active');
	$('#radio' + $(ww).data().interval.repeats).attr('checked', 'checked');
	$('label[for=radio' + $(ww).data().interval.repeats + ']').addClass('ui-state-active');
	var days = $(ww).data('interval')['every']['week'];
	for (var i = 0; i < days.length; i++){
		$('#repeat-dialog label.' + days[i]).addClass('ui-state-active');
		$('#repeat-dialog input.' + days[i]).attr('checked', 'checked');
	}
	$('#dialog-date').val($(ww).data().interval.until);
	$('#repeat-summary').html($(ww).data('summary'));
	

	$('#repeat-dialog').click(function(){
		// parse the repeat form and update the summary
		$('#week-interval-days input:checked').each(function(){
				days.push($(this).val());
			});
		
		$('#repeat-summary').html($(ww).data('summary'));
		return;
	});

	// validate, strinify data into recurrence input
	var ok = {
		text : 'Ok',
		click : function(){
			console.log('validation!');
			var data = JSON.stringify($(ww).data());
			$('#recurrence').val(data);	
			$('#repeat-dialog').dialog("close");
		}
	};

	var cancel = {
		text : 'Cancel',
		click : function(){
			$(ww).find('.rec input').removeAttr('checked');
			$('#repeat-dialog').dialog("close");
		}
	};

	$('#repeat-dialog').dialog({
		modal     : true,
		minWidth  : 475,
		buttons   : [ok, cancel],
		resizable : false
	});
}


$('.when-where').each(function(){
	
	//date
	var date = $(this).find('.date');
	date.datepicker({ dateFormat: 'mm/dd/y' });
	$(this).data('date', date.val());

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
	var when_where_instance = this;
	$(this).find('.rec').click(function(){
		Unify.recurrence(when_where_instance);
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
