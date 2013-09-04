/**
 * Bulk Select for lists of events
 **/
var bulkSelectAll = function() {
    $('#bulk-select-all').click(function() {
        var selectAll = $(this),
            singleSelects = $('.field-bulk-select input');
        singleSelects.prop('checked', selectAll.is(':checked'));
    });
};

/**
 * Activate active nav tab when anchor is specified in url
 **/
var autoOpenTagByAnchor = function() {
    var anchor = window.location.hash.substring(1),
        tab = $('.nav-tabs li a[href="#'+ anchor +'"]').parent('li'),
        tabPane = $('#' + anchor);
    if (anchor !== null && tabPane.length > 0 && tabPane.hasClass('tab-pane')) {
        $('.nav-tabs li.active, .tab-pane.active').removeClass('active');
        tab.addClass('active');
        tabPane.addClass('active');
    }
};

/**
 * Toggle 'Delete Single Event' modal
 **/
var toggleModalDeleteEvent = function() {
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
};

/**
 * Calendar grid carousels
 **/
var calendarCarousels = function() {
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
};

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

/**
 * WYSIWYG Textarea Init
 **/
var initiateWysiwyg = function(textarea) {
    textarea.wysihtml5({
        "font-styles": true, // Font styling, e.g. h1, h2, etc. Default true
        "emphasis": true, // Italics, bold, etc. Default true
        "lists": true, // (Un)ordered lists, e.g. Bullets, Numbers. Default true
        "html": false, // Button which allows you to edit the generated HTML. Default false
        "link": true, // Button to insert a link. Default true
        "image": true, // Button to insert an image. Default true,
        "color": false, // Button to change color of font
        events: {
            "load": function() {
                // Make the 'Insert Link' button more obvious
                $('ul.wysihtml5-toolbar')
                    .find('li a[data-wysihtml5-command="createLink"]')
                    .html('<i class="icon-link"></i>');
                // Execute iframe, label name reassignments
                //accessibleEventDescription();
            }
        }
    });
};

/**
 * Reassign Event Desc. WYSIWYG label to iframe
 **/
var accessibleEventDescription = function() {
    var textarea = $('#id_event-description'),
        label = $('label[for="id_event-description"]'),
        iframe = label.parent().find('iframe');
    if (textarea.length > 0) {
        iframe.attr('id', textarea.attr('id') + '_iframe');
        label.attr('for', label.attr('for') + '_iframe');
    }
};

/**
 * Display wysiwyg without control bar
 **/
var initiateDisabledWysiwyg = function(textarea) {
    textarea.wysihtml5({"font-styles": false, //Font styling, e.g. h1, h2, etc. Default true
                        "emphasis": false, //Italics, bold, etc. Default true
                        "lists": false, //(Un)ordered lists, e.g. Bullets, Numbers. Default true
                        "html": false, //Button which allows you to edit the generated HTML. Default false
                        "link": false, //Button to insert a link. Default true
                        "image": false, //Button to insert an image. Default true,
                        "color": false //Button to change color of font
    });
};

/**
 * Display wysiwyg without control bar
 **/
var initiateReReviewCopy = function() {
    $('#copy_title').click(function(e) {
        e.preventDefault();
        $('#' + $(this).attr('data-copy-to')).val($('#new_title').val());
    });

    $('#copy_description').click(function(e) {
        e.preventDefault();
        $('#' + $(this).attr('data-copy-to')).data('wysihtml5').editor.setValue($('#new_description').val());
    });
};

/**
 * User search typeahead
 **/
var userSearchTypeahead = function() {
    var inputField = $('#id_add_user'),
        resultList = inputField.next($('.typeahead.dropdown-menu')),
        timer = null,
        delay = 700;

    // Get all existing users in user list
    var existingUsers = function() {
        var array = [];
        $('.calendar-access-username:not("th")').each(function() {
            array.push($(this).html());
        });
        return array;
    };

    // Show retrieved results in a list below the input field
    var displayResults = function(response) {
        // Kill any previous input field styling
        inputField.removeClass('warning success');
        // Remove any existing results
        resultList.children('li').remove();
        // Display the list of successful results
        var results = response;
        for (i=0; i<results.length; i++) {
            var result = results[i],
            // Results are a list: first_name, last_name, username
                firstname = result[0],
                lastname = result[1],
                username = result[2];
            // Add result to list if username is not in list of existing calendar users
            if ($.inArray(username, existingUsers()) === -1) {
                resultList
                    .append('<li data-first_name="' + firstname + '" data-last_name="' + lastname + '" data-username="' + username + '"><a href="#">' + firstname + ' ' + lastname + ' (' + username + ')</a></li>')
                    .show();
            }
        }
        // Assign click event to new list items
        resultList
            .find('li > a')
            .click(function(e) {
                e.preventDefault();
                var result = $(this).parent('li'),
                    username = result.attr('data-username');
                // Populate hidden field values; force triggering of 'change' action
                $('#id_username')
                    .val(username)
                    .trigger('change');
                // Update the input field; make it look successful
                inputField
                    .val(firstname + ' ' + lastname)
                    .addClass('success');
                // Hide the result list
                resultList.hide();
            });
    };

    // Execute a search
    var performSearch = function(query) {
        $.ajax({
            url: 'http://' + HTTPHOST + '/manager/search/user/' + query,
            type: 'post',
            success: function(response) {
                displayResults(response);
            },
            error: function() {
                // Give the user a visual response that nothing came back
                inputField.addClass('warning');
                $('#id_username').val('');
                resultList.children('li').remove();
            }
        });
    };

    // Handle typing into search field
    inputField.keyup(function() {
        clearTimeout(timer);
        var query = inputField.val();
        timer = setTimeout(function() {
            // Execute a search for a non-empty field val
            if (query !== '') {
                performSearch(query);
            }
            // Remove an existing username value if the user cleared a name
            else {
                $('#id_username').val('');
            }
        }, delay);
    });
};

/**
 * Add new user front-end validation
 * (Don't allow new users to be submitted w/o valid name, role)
 **/
var userAddValidation = function() {
    var addBtn = $('#add-user-submit'),
        inputField = $('#id_add_user');

    // Click handler for easy toggling of link enable/disable
    var handler = function(e) {
        e.preventDefault();
    };

    // Check for changes in input values; toggle button
    var toggleAddBtn = function() {
        if (
            $('#id_add_user').val() === '' ||
            $('#id_username').val() === '' ||
            $('#id_add_role').val() === ''
        ){
            addBtn
                .addClass('disabled')
                .bind('click', handler);
        }
        else {
            addBtn
                .removeClass('disabled')
                .unbind('click', handler);
        }
    };

    // Handle load, on form change events
    toggleAddBtn();
    $('#id_add_user, #id_username, #id_add_role').change(function() {
        toggleAddBtn();
    });

    // Handle form submit
    addBtn.click(function(e) {
        if ($(this).hasClass('disabled') === false) {
            var form = $('#manager-calendar-add-user'),
                url = addBtn.attr('data-url'),
                username = $('#id_username').val(),
                role = $('#id_add_role').val();
            url = url.replace('/username/role', '/' + username + '/' + role);
            addBtn.attr('href', url);
        }
    });
};

/**
 * Clone fieldsets of a form; auto-increment field IDs as necessary.
 **/
var cloneableFieldsets = function() {
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
                // Add event handler for location autocomplete
                eventLocationsSearch($(row).find('.location-dropdown'));

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

        // On load
        toggleRemoveBtn(prefix);

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
};

/**
 * Update Calendar Ownership Reassignment url value in modal;
 * enable/disable submit button
 **/
var calendarOwnershipModal = function() {
    if ($('#calendar-reassign-ownership')) {
        var modal = $('#calendar-reassign-ownership');
        var submitBtn = modal.find('.modal-footer a.btn:first-child');
        submitBtn.click(function() {
            var newOwner = $('#new-owner-select').val(),
                url = submitBtn.attr('href');
            if (newOwner !== '') {
                url = url.replace(/user\/[A-Za-z0-9]+$/, 'user/' + newOwner);
                submitBtn.attr('href', url);
            }
        });
    }
};

/**
 * Toggle recurrences in Dashboard event list
 **/
var toggleEventListRecurrences = function() {
    $('.recurrences-toggle').click(function(e) {
        e.preventDefault();
        $(this).next('.recurrences').slideToggle();
    });
};

/**
 * Create/Update Event location searching + creation
 * Arg: $('select.location-dropdown')
 **/
var eventLocationsSearch = function(locationDropdowns) {
    if (locationDropdowns.length > 0) {
        locationDropdowns.each(function() {
            var dropdown = $(this);
            var autocompleteId = dropdown.attr('id') + '-autocomplete';

            // Hide dropdown
            dropdown.hide();

            // Create search as you type field, if necessary
            var locationAutocomplete = null,
                suggestionList = null;

            if (dropdown.siblings('.location-autocomplete').length < 1) {
                locationAutocomplete = $('<input type="text" id="'+ autocompleteId +'" class="location-autocomplete search-query" autocomplete="off" placeholder="Type a location name..." />');
                locationAutocomplete.insertAfter(dropdown);

                suggestionList = $('<ul class="dropdown-menu location-suggestions"></ul>');
                suggestionList.insertAfter(locationAutocomplete).hide();
            }
            else {
                locationAutocomplete = dropdown.siblings('.location-autocomplete');
                suggestionList = dropdown.siblings('.location-suggestions');
            }

            // Reassign dropdown label to autocomplete field
            dropdown.siblings('label[for*="-location"]').attr('for', autocompleteId);

            // Hide location remove btn if necessary
            if (dropdown.parents('.row').find('.location-selected-name').text() == '') {
                dropdown.parents('.row').find('.locations-selected-remove').hide();
            }

            // Perform a search + show suggestion list
            var autocompleteSearch = function(query) {
                var matchesFound = false;
                var matches = [];

                $.each(eventLocations, function(location, locationVals) {
                    if (location.toLowerCase().indexOf(query.toLowerCase()) > -1) {
                        // Push comboname to autocomplete suggestions list
                        matchesFound = true;
                        var listItem = $('<li data-location-id="' + locationVals.id + '" data-location-name="' + locationVals.name + '" data-location-room="' + locationVals.room + '" data-location-url="' + locationVals.url + '"><a tabindex="0" class="suggestion-link" href="#">' + location + '</a></li>');
                        matches.push(listItem);
                    }
                });
                if (matchesFound == true) {
                    // Append matches to list
                    $.each(matches, function(index, val) {
                        val.appendTo(suggestionList);
                    });
                    suggestionList.show();
                }
            }

            // Prevent form submission via enter keypress in autocomplete field
            dropdown.parents('form').on('submit', function(event) {
                if ($('.location-autocomplete').is(':focus')) {
                    return false;
                }
            });

            // Handle typing into search field
            var timer = null;
            var delay = 300;

            locationAutocomplete.on('keyup focus', function(event) {
                clearTimeout(timer);
                var query = locationAutocomplete.val();
                
                // Execute a search for a non-empty field val.
                // Searches eventLocations object (created in template.)
                if (query !== '') {
                    // Detect standard alphanumeric chars (and onfocus event)
                    if (
                        (event.type == 'focus') ||
                        (event.type == 'keyup' && event.keyCode !== 8 && event.keyCode > 44)
                    ) {
                        timer = setTimeout(function() {
                            suggestionList.empty();
                            autocompleteSearch(query);
                        }, delay);
                    }
                    // If user typed a non-alphanumeric key, check for up/down strokes
                    else if (event.type == 'keyup' && event.keyCode > 36 && event.keyCode < 41) {
                        if (suggestionList.children().length > 0) {
                            var newselected = null;
                            if (event.keyCode == 40) {
                                // Move down one list item. Check if a list item is highlighted yet or not
                                if (suggestionList.children('.selected').length > 0) {
                                    newselected = ($('.selected').next('li').length !== 0) ? $('.selected').next('li') : suggestionList.children('li').first();
                                }
                                else {
                                    newselected = suggestionList.children('li').first();
                                }
                            }
                            else if (event.keyCode == 38) {
                                // Move up one list item
                                if (suggestionList.children('.selected').length > 0) {
                                    newselected = ($('.selected').prev('li').length !== 0) ? $('.selected').prev('li') : suggestionList.children('li').last();
                                }
                                else {
                                    newselected = suggestionList.children('li').last();
                                }
                            }
                            else if (event.keyCode == 39 || event.keyCode == 37) {
                                // Left/right key press; do nothing
                                return;
                            }
                            suggestionList.children('li.selected').removeClass('selected');
                            newselected.addClass('selected');
                            locationAutocomplete.val(newselected.attr('data-location-name'));
                        }
                    }
                    // If user hit enter on the autocomplete field, select the query
                    else if (event.type == 'keyup' && event.keyCode == 13) {
                        // We can only select queries that are currently highlighted
                        if (suggestionList.children().length > 0) {
                            if (suggestionList.children('.selected').length < 1) {
                                selectSuggestion(suggestionList.children('li').first());
                            }
                            else {
                                selectSuggestion(suggestionList.children('.selected').first());
                            }
                        }
                    }
                }
                // Remove suggestion list if user emptied the field
                else {
                    suggestionList.empty().hide();
                }

            });

            var selectSuggestion = function(listItem) {
                var row = listItem.parents('.row');
                row.find('.location-selected-name').text(listItem.attr('data-location-name'));
                row.find('.location-selected-room').text(listItem.attr('data-location-room'));
                row.find('.location-selected-url').text(listItem.attr('data-location-url'));
                suggestionList.empty().hide();
                dropdown.children('option[selected="selected"]').attr('selected', false);
                dropdown.children('option[value="' + listItem.attr('data-location-id') + '"]').attr('selected', true);
                row.find('.location-selected-remove').show();
                locationAutocomplete.val('');
            };

            var unselectSuggestion = function(removeBtn) {
                removeBtn.siblings('span').text('');
                dropdown.children('option[selected="selected"]').attr('selected', false);
                dropdown.children('option[value=""]').attr('selected', true);
            };

            // Handle selection of a suggestion
            $('body').on('click', '.suggestion-link', function(event) {
                event.preventDefault();
                selectSuggestion($(this).parent('li'));
            });

            // Handle removal of a selected suggestion
            $('.location-selected-remove').on('click', function(event) {
                event.preventDefault();
                unselectSuggestion($(this));
                $(this).hide();
            });
        });
    }
};


$(document).ready(function() {
    bulkSelectAll();
    autoOpenTagByAnchor();
    toggleModalDeleteEvent();
    calendarCarousels();
    initiateDatePickers($('.field-date'));
    initiateTimePickers($('.field-time'));
    initiateWysiwyg($('textarea.wysiwyg:not(".disabled-wysiwyg")'));
    //accessibleEventDescription();
    initiateDisabledWysiwyg($('textarea.wysiwyg.disabled-wysiwyg'));
    initiateReReviewCopy();
    userSearchTypeahead();
    userAddValidation();
    cloneableFieldsets();
    calendarOwnershipModal();
    toggleEventListRecurrences();
    eventLocationsSearch($('select.location-dropdown'));
});
