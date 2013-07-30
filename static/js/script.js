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
