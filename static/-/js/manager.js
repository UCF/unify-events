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
Unify.recurrence = function(){
	
	/*** convert the recurrence data to some sort of readerable engrish ***/
	var update_summary = function(){
		var ww = Unify.recur_focus;
		var ordinal = function(x) {
			num = new Number(x);
			num = num.toString();
			var end_num = num.charAt(num.length - 1);
			var start_num = num.charAt(0);
			var abbrev = 'th';
			if (end_num == '1' && start_num != '1') abbrev = 'st';
			if (end_num == '2' && start_num != '1') abbrev = 'nd';
			if (end_num == '3' && start_num != '1') abbrev = 'rd';
			return num + abbrev;
		};
		var txt;
		switch($(ww).data().interval.repeats){
			case 'week':
				var days = $(ww).data().interval.every.week;
				txt = "Repeats every " + days.join(', ');
				break;
			case 'month':
				var dayof = $(ww).data().interval.every.month;
				var date = $(ww).data().date;
				if(dayof == 'dayofmonth'){
					var num = date.getDate();
					txt = 'Repeats montly the ' + ordinal(num);
				} else { // day of week
					var num = date.getDate();
					var week_num = Math.floor(num/7);
					var day = $.datepicker.formatDate('DD', date);
					txt = "Repeats on the " + ordinal(week_num) + " " + day + " of every month"
				}
				break;
		}
		txt += " until " + $(ww).data().interval.until;
		$(ww).data().summary = txt;
		$('#repeat-summary').html(txt);
		return txt;
	};

	/*** parse the event's recurrence data ***/
	var ww = Unify.recur_focus;
	var txt = $(ww).find('input.date').val();
	var date = $.datepicker.parseDate('mm/dd/y', txt);
	var repeats, dayof, until;
	var days = new Array();
	var interval = JSON.parse($(ww).find('.recurrence').val());
	if(interval){
		repeats = interval.repeats;
		days    = interval.every.week;
		dayof   = interval.every.month;
		until   = interval.until;
	} else {
		// create interval data with defaults
		repeats = 'week';
		var txt = $(ww).find('.date').val();
		var day = $.datepicker.formatDate('D', date);
		days  = new Array(day);
		until = new Date();
		var six_mo = 1000*60*60*24*183;
		until.setTime(date.getTime() + six_mo);
		until = $.datepicker.formatDate('mm/dd/y', until);
	}
	$(ww).data({
		'date'     : date,
		'interval' : {
			'repeats' : repeats, // week or month
			'every'   : { 'week' : days, 'month': dayof }, //dayof = dayofweek or dayofmonth
			'until'   : until
		}
	});

	/*** fill repeat dialog with data ***/
	
	// clear form
	$('#repeat-dialog input').removeAttr('checked').removeAttr('selected');
	$('#repeat-dialog label').removeClass('ui-state-active');
	
	// fill repeats radio buttons
	$('#radio' + repeats).attr('checked', 'checked');
	$('label[for=radio' + repeats + ']').addClass('ui-state-active');
	
	// for weekly, fill days selected
	for (var i = 0; i < days.length; i++){
		$('#repeat-dialog input.' + days[i]).attr('checked', 'checked');
		$('#repeat-dialog label.' + days[i]).addClass('ui-state-active');
	}

	// for montly, select type
	$('#dayof' + repeats).attr('checked', 'checked');
	console.log('#dayof' + repeats);
	$('label[for=dayof' + repeats + ']').addClass('ui-state-active');
	
	// until date and summary
	$('#dialog-date').val(until);
	update_summary(ww);
	
	// "repeat on" week/month table row toggle
	var toggle_repeats = function(){
		var ww = Unify.recur_focus;
		$('#repeats-week, #repeats-month').hide();
		$('#repeats-' + $(ww).data().interval.repeats).show();
	}
	toggle_repeats();


	/*** onclick, update data, display, and summary ***/
	var update_data_display = function(){
		var ww = Unify.recur_focus;
		if(!$(ww).data().interval || !$(ww).data().interval.every){
			console.log('error - bad dad data in recurrence');
			return;
		}
		var repeat = $('input[name=repeats]:checked').val();
		var days   = $(ww).data().interval.every.week;
		var dayof  = $(ww).data().interval.every.month;
		switch(repeat){
			case 'week':
				days = new Array();
				$('#week-days input:checked').each(function(){
					days.push($(this).val());
				});
				break;
			case 'month':
				var dayof = $('input[name=dayof]:checked').val();
				break;
		}
		var until = $('#dialog-date').val();
		$(ww).data().interval = {
			'repeats' : repeat,
			'every'   : { 'week' : days, 'month': dayof },
			'until'   : until
		};
		toggle_repeats();
		update_summary();
		return;
	};
	$('#repeat-dialog').click(function(){
		update_data_display();
	});
	$('#dialog-date').change(function(){
		update_data_display();
		var ww = Unify.recur_focus;
		var until = $.datepicker.parseDate('mm/dd/y', $(this).val());
		var diff = until.getTime() - $(ww).data().date.getTime();
		var year = 1000*60*60*24*365;
		$('#repeat-dialog .error').remove();
		if(diff<0){
			$(this).before('<div class="error">This date is before the event\'s date</div>');
			return false;
		} 
		if(diff>year){
			$(this).before('<div class="error">An event can only repeat for one year max.</div>');
			return false;
		}
		return true;
	});


	/*** validate then strinify data into recurrence input ***/
	var ok = {
		text : 'Ok',
		click : function(){
			var ww = Unify.recur_focus;
			// this is where more validation should happen
			if($('#repeat-dialog .error').length > 0){
				alert('Please correct errors or cancel repeat.');
				return false;
			}
			var data = JSON.stringify($(ww).data('interval'));
			$(ww).find('.recurrence').val(data);
			var summary = $(ww).data().summary;
			$(ww).find('.rec').hide();
			$(ww).find('.summary span').html(summary);
			$(ww).find('.summary').show();
			$('#repeat-dialog').dialog("close");
		}
	};
	var cancel = {
		text : 'Cancel',
		click : function(){
			$('#repeat-dialog .error').remove();
			$('#repeat-dialog').dialog("close");
		}
	};
	var clear = {
		text : 'Clear',
		className : 'clear-all',
		click : function(){
			var ww = Unify.recur_focus;
			var sure = confirm('are you sure you want to clear all recurrance?');
			if(sure){
				$('#repeat-dialog .error').remove();
				$(ww).find('.recurrence').val(false);
				$('#repeat-dialog').dialog("close");
				$(ww).find('.summary').hide();
				$(ww).find('.rec').show();
			}
		}
	};

	$('#repeat-dialog').dialog({
		modal     : true,
		minWidth  : 475,
		minHeight : 300,
		buttons   : [clear, ok, cancel],
		resizable : false
	});

	return false;

} // recurrence


/******************************************************************************\
  When / Where, add a new instance
\******************************************************************************/
Unify.wwi = 0; // when where index / count
Unify.wwInit = function(instance){
	var selector = instance || '.when-where:first';
	$(selector).each(function(){
		
		//date
		var date = $(this).find('.date');
		date.datepicker({ dateFormat: 'mm/dd/y' });
		
		//end time
		var end = $(this).find('.end');
		var add = $(this).find('.add.end-time').click(function(){
			$(this).hide();
			end.show();
		});
		$(this).find('.remove.rm-time').click(function(){
			add.show()
			end.hide();
		});

		//select time
		var d = new Date();
		var h = d.getHours();
		var time = h + ":00";
		var find = function() { return $(this).text() === time; }
		$(this).find('option').filter(find).attr('selected', 'selected');

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
		$(this).find('.rec, .summary a').click(function(e){
			e.stopPropagation();
			$(this).find('input').removeAttr('checked');
			Unify.recur_focus = when_where_instance;
			Unify.recurrence();
		});

		// delete
		$(this).find('.delete').click(function(){
			$(this).parent().remove();
			Unify.wwi -= 1;
			if(Unify.wwi < 1) $('.when-where .delete').hide();
		});
		
	});
}
Unify.wwInit();

$('#when-where-add').click(function(){
	var ww = $('.when-where:eq('+Unify.wwi+')');
	var html = $('#when-where-template').html();
	var new_ww = $(html);
	$(ww).after(new_ww);
	$('.when-where .delete').show();
	Unify.wwInit(new_ww);
	Unify.wwi += 1;
});

/******************************************************************************\
  Tags
\******************************************************************************/
$.fn.toggleAttr = function(att){
	return this.each(function(){
		var el = $(this);
		if(el.attr(att)) el.removeAttr(att);
		else el.attr(att,att);
		console.log('toggle yo', el.attr(att), att, el);
	});
};

Unify.tags = function(tag){
	var selector = tag || '#tags label';
	$(selector).each(function(){
		var update = function(){
			// update all label classes, works for radios and checkboxes
			$(this).parents('ul').find('label').each(function(){
				var on = ($(this).find('input:checked').length > 0);
				if(on) $(this).addClass('selected');
				else $(this).removeClass('selected');
			})
		}
		$(this).click(update);
		$(this).each(update);
	});
}
Unify.tags();
$('#tags li > a').click(function(){
	// create a new tag
	var new_tag = $('<li class="new"><label><input type="text"><a>close</a></label></li>');
	new_tag.find('a').click(function(){
		$(this).parents('li').remove();
	});
	$(this).parent().before(new_tag);
	var update_width = function(){
		var txt = $(this).val();
		var width = $('#tag-test').html(txt).width();
		width += 5;
		if(txt.length>35) $(this).parent().addClass('error');
		else $(this).parent().removeClass('error');
		if(width<50) width = 50;
		if(width>450) width = 450;
		$(this).width(width);	
	};
	new_tag.find('input')
		.focus()
		.keydown(update_width)
		.keyup(update_width)
		.blur(function(){
			if($(this).val().length<2) $(this).parent().addClass('error');
			else if($(this).val().length<=35) $(this).parent().removeClass('error');
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
