var slider_track_html = '<div class="slider-track"></div>';
var slider_html       = '<div class="slider"><!-- --></div>';

(function($){
	$.fn.slider = (function(arguments){
		var defaults = {
			'cycle_length'     : 6000,
			'animation_length' : 2000
		};
		var options      = $.extend({}, defaults, arguments);
		var container    = $(this);
		var slider_track = $(slider_track_html);
		var slider       = $(slider_html);
		var mousetracker = null;
		
		//Initialize html and styles
		(function(){
			slider_track.innerWidth(container.innerWidth());
			slider_track.append(slider);
			container.after(slider_track);
			var width = 0;
			container.children().each(function(){
				width += $(this).outerWidth();
			});
			container.css({
				'overflow'
				'width' : width + 'px'
			});
		})();
		
		slider_track.mousedown(function(){
			
		});
		
		slider.mousedown(function(e){
			var mouse_origin  = e.pageX;
			var slider_origin = slider.position().left;
			
			//Use active state of background-image
			slider.css({
				'background-position' : '-' + slider.width(),
				'position'            : 'relative'
			});
			//Update position on mouse move
			$(document).mousemove(function(e){
				//get current mouse position
				var mouse = e.pageX;
				//find difference from mouse origin
				var diff = mouse - mouse_origin;
				//apply difference to slider origin
				var update = slider_origin + diff - slider.width();
				
				console.log(update, slider_track.innerWidth());
				
				if (update < 0){
					update = 0;
				}
				if (update + slider.width() > slider_track.innerWidth()){
					update = slider_track.innerWidth() - slider.width();
				}
				slider.css({'left' : update});
			});
		
			$(document).mouseup(function(e){
				$(document).unbind('mousemove');
				$(document).unbind(e);
			});
		});
		
	});
	
	
	$.fn.imageRotate = (function(arguments){
		var defaults = {
			'fade_length'  : 2000,
			'image_length' : 6000
		};
		var options   = $.extend({}, defaults, arguments);
		var container = $(this);
		
		var active = container.children('img.active');
		if (active.length < 1){
			active = container.children('img:last');
			active.addClass('active');
		}
		
		var next = active.next();
		if (next.length < 1){
			next = container.children('img:first');
		}
		
		active.addClass('last-active');
		next.css({'opacity' : 0.0});
		next.addClass('active');
		next.animate({'opacity': 1.0}, options.fade_length, function(){
			active.removeClass('active last-active');
		});
		
		setTimeout(function(){container.imageRotate(options);}, options.image_length);
	});
	
	$('.slideshow').slider({});
})(jQuery)