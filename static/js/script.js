$('document').ready(function() {
    /**
     * Sidebar Mini calendars
     **/
    $('#sidebar-minicals').on('slid', function() {
    	var firstItem = $('#sidebar-minicals .carousel-inner .item:first-child'),
    		lastItem  = $('#sidebar-minicals .carousel-inner .item:last-child'),
    		controlNext = $('#sidebar-minicals .pager .next'),
    		controlPrev = $('#sidebar-minicals .pager .previous');
    
    	if (firstItem.hasClass('active')) {
    		controlPrev
    			.addClass('disabled')
    			.find('a')
    				.attr('href', '');
    	}
    	else {
    		controlPrev
    			.removeClass('disabled')
    			.find('a')
    				.attr('href', '#sidebar-minicals');
    	}
    	if (lastItem.hasClass('active')) {
    		controlNext
    			.addClass('disabled')
    			.find('.carousel-control.right')
    				.attr('href', '');
    	}
    	else {
    		controlNext
    			.removeClass('disabled')
    			.find('.carousel-control.right')
    				.attr('href', '#sidebar-minicals');
    	}
    });
    
    $('.disabled').click(function(e) {
    	e.preventDefault();
    });
    
    
    /**
     * Date/Timepicker Init
     **/
    $('.field-date').datepicker({
        format:'yyyy-mm-dd'
    });
    $('.field-time')
        .each(function(){
            $(this)
                .next('span.add-on')
                .andSelf()
                .wrapAll('<div class="input-append bootstrap-timepicker" />')
        }).timepicker();
        
        
    /**
     * WYSIWIG Textarea Init
     **/
    $('textarea.wysiwyg').wysihtml5();
});
