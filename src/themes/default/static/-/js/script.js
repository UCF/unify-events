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

Webcom.calendarWidget = function($){
	$('.calendar-widget .month-controls a').click(function(){
 		var url    = $(this).attr('href');
		var parent = $(this).parents('.calendar-widget');
		$.ajax(url, {
			'success' : function(data){
				var replace = $(data);
				parent.replaceWith(replace);
				bind_func($);
			}
		});
		return false;
	});
	
	$('.calendar-widget .day a').click(function(){
		var elements_to_update = ['.subscribe-widget', '#left-column'];
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
				bind_func($);
			}
		});
		
		return false;
	});
	
	
	$('.full-calendar .day a').unbind('click');
	$('.full-calendar .month-controls a').unbind('click');
	$('.full-calendar .month-controls a').click(function(){
 		var url    = $(this).attr('href');
		var parent = $(this).parents('.calendar-widget');
		$.ajax(url, {
			'success' : function(data){
				var replace = $(data);
				parent.replaceWith(replace);
				
				var title = '';
				try{
					title = data.match(/<title>([^<]*)<\/title>/)[1];
				}catch(e){}
				url = url.replace('widget/', '');
				url = url.replace('?html_class=full-calendar', '');
				
				history.pushState({}, title, url);
				bind_func($);
			}
		});
		return false;
	});
};

var bind_func = function ($){
	$('*').unbind();
	Webcom.calendarWidget($);
	
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
}

$().ready(function(){
	bind_func(jQuery);
});