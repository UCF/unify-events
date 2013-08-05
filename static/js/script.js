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
    var initiateDatePickers = function(field) {
        field.datepicker({
            format:'yyyy-mm-dd'
        });
    };
    var initiateTimePickers = function(field) {
        var date = new Date();
        var time = date.getHours() + ':' + date.getMinutes();
        field
            .each(function(){
                // Wrap each timepicker input if this field isn't a clone
                if ($(this).parent().hasClass('bootstrap-timepicker') === false) {
                    $(this)
                        .attr('placeholder', time)
                        .next('span.add-on')
                        .andSelf()
                        .wrapAll('<div class="input-append bootstrap-timepicker" />');
                }
            }).timepicker({
                showMeridian: false,
                defaultTime: false
            });
    };
    $(document).ready(function() {
        initiateDatePickers($('.field-date'));
        initiateTimePickers($('.field-time'));
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
    };
    userSearchTypeahead();


    /**
     * Clone fieldsets of a form; auto-increment field IDs as necessary.
     **/
    if ($('.cloneable').length > 0) {
        var cloneableWrap = $('.cloneable').parent(),
            cloneable = cloneableWrap.children(':first'),
            cloneBtn = cloneableWrap.parent().find('.cloner'),
            prefix = cloneable.attr('data-form-prefix');

        // Update the index in the ID, name, or 'for' attr of the form element
        var updateElementIndex = function(element, prefix, index) {
            var id_regex = new RegExp('(' + prefix + '-\\d+-)');
            var replacement = prefix + '-' + index + '-';
            if ($(element).attr('for')) {
                $(element).attr('for', $(element).attr('for').replace(id_regex, replacement));
            }
            if (element.id) {
                element.id = element.id.replace(id_regex, replacement);
            }
            if (element.name) {
                element.name = element.name.replace(id_regex, replacement);
            }
        };

        var toggleRemoveBtn = function(prefix) {
            // Toggle the 'hidden' class off of each cloneable element
            // if there are more than one cloneables on the screen
            if ($('#id_' + prefix + '-TOTAL_FORMS').val() == 1) {
                cloneableWrap.find('.remove-instance').addClass('hidden');
            }
            else {
                cloneableWrap.find('.remove-instance').removeClass('hidden');
            }
        };

        // Delete a cloneable element
        var deleteForm = function(btn, prefix) {
            var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val(), 10);
            if (formCount > 1) {
                // Delete the cloneable
                $(btn).parents('.cloneable').slideUp(300);
                setTimeout(function() {
                    // Remove deleted cloneable; update totals/indexes after removal
                    $(btn).parents('.cloneable').remove();

                    var forms = $('.cloneable'); // Get all the cloneable items

                    // Update the total number of cloneables (1 less than before)
                    $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);

                    var i = 0;
                    // Go through the cloneables and set their indexes, names and IDs
                    for (formCount=forms.length; i<formCount; i++) {
                        $(forms.get(i))
                            .find('input, textarea, select, label')
                            .each(function () {
                                updateElementIndex(this, prefix, i);
                        });
                    }

                    // Toggle remove buttons, if necessary
                    toggleRemoveBtn(prefix);
                }, 300);
            }
            return false;
        };

        // Clone a cloneable element
        var addForm = function(btn, prefix) {
            var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val(), 10);

            // You can only submit a maximum of 12 instances
            if (formCount < $('#id_' + prefix + '-MAX_NUM_FORMS').val()) {
                // Clone a form from the first form
                var row = cloneable.clone(false).get(0);

                $(row)
                    // Insert it after the last form
                    .removeAttr('id')
                    .hide()
                    .insertAfter('.cloneable:last')
                    .slideDown(300)
                    // Relabel or rename all the relevant bits
                    .find('input, textarea, select, label')
                    .each(function () {
                        updateElementIndex(this, prefix, formCount);
                        $(this).val('');
                });

                // Add an event handler for the delete item/form link 
                $(row).find('.remove-instance').click(function () {
                    return deleteForm(this, prefix);
                });
                // Add event handlers for date/time widgets
                initiateDatePickers($(row).find('.field-date'));
                initiateTimePickers($(row).find('.field-time'));

                // Update the total form count
                $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);

                // Toggle remove buttons, if necessary
                toggleRemoveBtn(prefix);
            }
            else {
                alert('Sorry, you can only create a maximum of twelve time/locations.');
            }
            return false;
        };

        // Register the click event handlers
        cloneBtn.click(function(e) {
            e.preventDefault();
            return addForm(this, prefix);
        });
        $('.remove-instance').click(function(e) {
            e.preventDefault();
            return deleteForm(this, prefix);
        });


    }
    

});
