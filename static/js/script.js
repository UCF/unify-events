$('document').ready(function() {
    /**
     * Bulk Select for lists of events
     **/
    $('#bulk-select-all').click(function() {
        var selectAll = $(this),
            singleSelects = $('.field-bulk-select input');
        singleSelects.prop('checked', selectAll.is(':checked'));
    });


    /**
     * Activate active nav tab when anchor is specified in url
     **/
    var anchor = window.location.hash.substring(1),
        tab = $('.nav-tabs li a[href="#'+ anchor +'"]').parent('li'),
        tabPane = $('#' + anchor);
    if (anchor !== null && tabPane.length > 0 && tabPane.hasClass('tab-pane')) {
        $('.nav-tabs li.active, .tab-pane.active').removeClass('active');
        tab.addClass('active');
        tabPane.addClass('active');
    }


    /**
     * Delete Single Event modal toggle
     **/
    $('.event-delete').click(function(e) {
        e.preventDefault();
        var modal       = $('#event-delete-modal'),
            eventTitle  = $(this).attr('data-event-title'),
            deleteURL   = $(this).attr('href');
        modal
            .find('h2 span.alt')
                .text(eventTitle)
                .end()
            .find('.modal-footer a.btn-danger')
                .attr('href', deleteURL)
                .end()
            .modal('show');
    });
    

    /**
     * Calendar grid carousels
     **/
    $('.calendar-slider').on('slid', function() {
    	var firstItem = $('.calendar-slider .carousel-inner .item:first-child'),
    		lastItem  = $('.calendar-slider .carousel-inner .item:last-child'),
    		controlNext = $('.calendar-slider .pager .next'),
    		controlPrev = $('.calendar-slider .pager .previous'),
            sliderID = $(this).attr('id');
    
    	if (firstItem.hasClass('active')) {
    		controlPrev
    			.addClass('disabled')
    			.find('a')
    				.attr('href', '#');
    	}
    	else {
    		controlPrev
    			.removeClass('disabled')
    			.find('a')
    				.attr('href', '#' + sliderID);
    	}
    	if (lastItem.hasClass('active')) {
    		controlNext
    			.addClass('disabled')
    			.find('.carousel-control.right')
    				.attr('href', '#');
    	}
    	else {
    		controlNext
    			.removeClass('disabled')
    			.find('.carousel-control.right')
    				.attr('href', '#' + sliderID);
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
    var date = new Date();
    var time = date.getHours() + ':' + date.getMinutes();
    $('.field-time')
        .each(function(){
            $(this)
                .attr('placeholder', time)
                .next('span.add-on')
                .andSelf()
                .wrapAll('<div class="input-append bootstrap-timepicker" />')
        }).timepicker({
            showMeridian: false,
            defaultTime: false
        });
        
        
    /**
     * WYSIWIG Textarea Init
     **/
    $('textarea.wysiwyg').wysihtml5();


    /**
     * User search typeahead
     **/
    var userSearchTypeahead = function() {
        $('.typeahead.user-search')
            .each(function() {
                var field = $(this);
                field.typeahead({
                    source: function(query, process) {
                        return $.get(
                            field.attr('data-source') + query,
                            function(data) {
                                return process(data.username);
                            }
                        );
                    },
                    minLength: 3,
                });
            });
    }
    userSearchTypeahead();
    

});
