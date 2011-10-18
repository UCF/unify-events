var sluggify = function(s) {return s.toLowerCase().replace(/\s/g, '-').replace(/[^A-Za-z-]/, '');}
var Webcom   = {};

/*
 * Dynamically add items to formsets.
 * From: http://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset-with-ajax
 *
 */
function extend_formset(selector, type) {
	var newElement = $(selector).clone(true);
	var total = $('#id_' + type + '-TOTAL_FORMS').val();
	newElement.find(':input').each(function() {
		var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
		var id = 'id_' + name;
			$(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
	});
	newElement.find('label').each(function() {
		var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
			$(this).attr('for', newFor);
	});
	total++;
	$('#id_' + type + '-TOTAL_FORMS').val(total);
	$(selector).after(newElement);
}


/**
 * Handles various actions and behaviours for the variety of calendar widgets
 * througout the application
 **/
Webcom.calendarWidget = function($){
	$('.calendar-widget .month-controls a').live('click', function(){
 		var url    = $(this).attr('href');
		var parent = $(this).parents('.calendar-widget');
		$.ajax(url, {
			'success' : function(data){
				var replace = $(data);
				parent.replaceWith(replace);
			}
		});
		return false;
	});
	
	$('.calendar-widget .day a').live('click', function(){
		var elements_to_update = ['.subscribe-widget', '.left-column', '.browse-widget'];
		var url = $(this).attr('href');
		$.ajax(url, {
			'success' : function (data){
				var result = $(data);
				$.each(elements_to_update, function(){
					var find    = this.valueOf();
					var element = result.find(find);
					$(find).replaceWith(element);
				});
				
				var title = '';
				try{
					title = data.match(/<title>([^<]*)<\/title>/)[1];
				}catch(e){}
				history.pushState({}, title, url);
			}
		});
		
		return false;
	});
	
	
	var close_expanded_calendar = function(){
		var widget      = $('.expanded-calendar-container .calendar-widget');
		var container   = $('.expanded-calendar-container');
		var placeholder = $('.expanded-calendar-placeholder');
		var clone       = widget.clone();
		
		placeholder.replaceWith(clone);
		clone.addClass('.expanded-calendar-placeholder');
		
		container.animate({
			'top'    : clone.offset().top,
			'left'   : clone.offset().left,
			'width'  : 0,
			'height' : 0
		}, 500, 'linear', function(){
			$('.expanded-calendar-container').remove();
			$('.expanded-calendar-placeholder').replaceWith(widget);
		});
	};
	
	$('.calendar-widget .expand').live('click', function(){
		var duration    = 500;
		var expand      = $(this).offset();
		var widget      = $(this).parents('.calendar-widget');
		var cur_pos     = widget.offset();
		var cur_height  = widget.height();
		var container   = $('<div class="expanded-calendar-container"></div>');
		var placeholder = widget.clone();
		
		placeholder.addClass('expanded-calendar-placeholder');
		widget.replaceWith(placeholder);
		widget.show();
		container.append(widget);
		$('body').append(container);
		
		container.css({
			'top'      : expand.top - 50,
			'left'     : expand.left + 200,
			'width'    : '0px',
			'height'   : '0px',
			'z-index'  : 2
		});
		container.animate({
			'width' : '100%',
			'height': '100%',
			'left'  : 0,
			'top'   : '-=50px'
		}, duration, 'linear', function(){});
		
		$(document).keydown(function(e){
			//Escape
			if (e.keyCode == 27){
				close_expanded_calendar();
			}
		});
	});
	
	$('.expanded-calendar-container .calendar-widget .day a').live('click', function(){
		close_expanded_calendar();
	});
};


$().ready(function(){
	Webcom.calendarWidget($);
});