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
	
});