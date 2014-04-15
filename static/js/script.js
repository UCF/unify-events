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
 * Bulk action submit.
 **/
var bulkActionSubmit = function() {
    var bulkActionSelects = $('#bulk-action_0, #bulk-action_1');
    bulkActionSelects.removeAttr('onchange');
    $('#bulk-action_0, #bulk-action_1').change(function() {
        var bulkForm = this.form
            actionInput = $(this),
            actionInputValue = actionInput.find('option:selected'),
            eventsSelected = $('input:checkbox:checked[name="event_ids"]'),
            recurringEvents = false;

        if (!actionInputValue.attr('value') || !eventsSelected.length) {
            // Don't do anything if there isn't a value
            return;
        } else if (actionInputValue.val() == 'delete') {
            eventsSelected.each(function(index, element) {
                var checkbox = $(this);

                if (parseInt(checkbox.attr('data-event-instance-count')) > 1) {
                    recurringEvents = true;
                    return false;
                }
            });

            if (recurringEvents) {
                bulkEventDeleteModal = $('#bulk-event-delete-modal');
                bulkEventDeleteModal.find('#bulk-event-delete-btn').click(function() {
                    bulkForm.submit();
                })
                bulkEventDeleteModal.modal();
            } else {
                bulkForm.submit();
            }
        } else {
            bulkForm.submit();
        }
    })
}

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
 * Toggle Generic Object modification/deletion modal.
 *
 * Populates modal contents with the static form specified
 * in the toggle link's 'href' attribute.
 **/
var toggleModalModifyObject = function() {
    $('.object-modify').click(function(e) {
        e.preventDefault();

        var deleteBtn = $(this),
            staticPgUrl = deleteBtn.attr('href'),
            modal = $('#object-modify-modal');

        if (modal) {
            $.ajax({
                url: staticPgUrl,
                timeout: 600 // allow 6 seconds to pass before failing the ajax request
            })
                .done(function(html) {
                    // Assign returned html to some element so we can traverse the dom successfully
                    var markup = $('<div />');
                    markup.html(html);

                    var modalTitle = '',
                        modalBody = '',
                        modalFooter = '';

                    // Grab data from the requested page. Check it to make sure it's not
                    // an error message or something we don't want
                    if (markup.find('.object-modify-form').length > 0) {
                        modalTitle = markup.find('h1').html();
                        modalBody = markup.find('.modal-body-content').html();
                        modalFooter = markup.find('.modal-footer-content').html();
                    }
                    else {
                        modalTitle = 'Error';
                        modalBody = '<p>You do not have access to this content.</p>';
                        modalFooter = '<a class="btn" data-dismiss="modal" href="#">Close</a>';
                    }

                    modal
                        .find('h2')
                            .html(modalTitle)
                            .end()
                        .find('form')
                            .attr('action', staticPgUrl)
                            .end()
                        .find('.modal-body')
                            .html(modalBody)
                            .end()
                        .find('.modal-footer')
                            .html(modalFooter)
                            .end()
                        .modal('show');
                })
                .fail(function() {
                    // Just redirect to the static modify/delete page for the object
                    window.location = staticPgUrl;
                });
        }
        else { window.location = staticPgUrl; }
    });
};

/**
 * Toggle 'Merge Tag/Category' modal
 **/
var toggleModalMergeObject = function() {
    var modal = $('#object-merge-modal');

    $('.category-merge, .tag-merge, .location-merge').click(function(e) {
        e.preventDefault();

        var objectTitle = $(this).attr('data-object-title'),
            mergeURL    = $(this).attr('href');

        var objectType = '';
        if ($(this).hasClass('category-merge')) {
            objectType = 'category';
        }
        else {
            objectType = 'tag';
        }

        /* Remove selected object from list of all objects */
        modal
            .find('#new-object-select option')
                .each(function() {
                    if ($(this).text() == objectTitle) {
                        $(this).prop('disabled', true);
                    }
                    else {
                        /* Re-enable any previously disabled options from an old modal */
                        $(this).prop('disabled', false);
                    }
                });

        /* Insert object type/title in modal text */
        modal
            .find('span.object-type')
                .text(objectType)
                .end()
            .find('h2 span.alt')
                .text(objectTitle)
                .end()
            .find('.modal-footer a.btn-primary')
                .attr('href', mergeURL)
                .end()
            .modal('show');
    });

    var submitBtn = modal.find('.modal-footer a.btn:first-child');
    submitBtn.click(function() {
        var newObject = $('#new-object-select').val(),
            url = submitBtn.attr('href');
        if (newObject !== '') {
            url = url.replace(/merge\/[A-Za-z0-9]+$/, 'merge/' + newObject);
            submitBtn.attr('href', url);
        }
    });
};

/**
 * Calendar grid sliders
 **/
var calendarSliders = function() {
    $('body').on('click', '.calendar-slider ul.pager li a', function(e) {
        e.preventDefault();

        var slider = $(this).parents('.calendar-slider');
        $.get($(this).attr('data-ajax-link'), function(data) {
            slider.replaceWith(data);
        });
    });
};


/**
 * Helper function for determining browser support for <input> types.
 **/
var inputTypeSupport = function(type) {
    var dummyField = document.createElement('input');
    dummyField.setAttribute('type', type);
    if (dummyField.type == type) {
        return true;
    }
    return false;
}


/**
 * Date/Timepicker Init.
 * Use Bootstrap datepicker/jQuery timepicker plugins.
 **/
var initiateDatePickers = function(fields) {
    fields.each(function() {
        var field = $(this);

        // Wrap field in wrapper div; add icon
        if (field.parent().hasClass('bootstrap-datepicker') === false) {
            field
                .wrap('<div class="bootstrap-datepicker" />')
                .parent()
                .append('<i class="icon-calendar" />');
        }

        var fieldParent = field.parent().parent();
        var siblingDateField = fieldParent.siblings().find('.' + field.attr('class'));

        field
            .datepicker({
                format: 'mm/dd/yyyy',
                autoclose: true,
                todayHighlight: true
            })
            .on('changeDate', function(e) {
                // Look for a nearby related start/end date field.  Apply
                // fixed start/end dates to the opposing fields, if possible.
                if (siblingDateField.length && fieldParent.hasClass('start')) {
                    siblingDateField.datepicker('setStartDate', e.date);
                }
                else if (siblingDateField.length && fieldParent.hasClass('end')) {
                    siblingDateField.datepicker('setEndDate', e.date);
                }
            });
    });

};
var initiateTimePickers = function(fields) {
    fields
        .each(function(){
            // Wrap each timepicker input if this field isn't a clone
            if ($(this).parent().hasClass('bootstrap-timepicker') === false) {
                $(this)
                    .wrap('<div class="bootstrap-timepicker" />')
                    .parent()
                    .append('<i class="icon-time" />');
            }
        })
        .timepicker({
            'scrollDefaultNow': true,
            'timeFormat': 'h:i A',
            'step': 15
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
                        .html('<i class="icon-link"></i>')
                        .end()
                    .find('li.dropdown a')
                        .attr('tabindex', '-1');
            }
        }
    });
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
            type: 'get',
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
                $(btn)
                    .parents('.cloneable')
                        .slideUp(300)
                        .find('input[id*="-DELETE"]')
                            .prop('checked', true);

                setTimeout(function() {
                    // Remove deleted cloneable; update totals/indexes after removal
                    if ($(btn).parents('.cloneable').find('input[id$="-id"]').val() == '') {
                        $(btn).parents('.cloneable').remove();
                    }

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
                    .addClass('clone')
                    .hide()
                    .insertAfter('.cloneable:last')
                    .slideDown(300)
                    // Relabel or rename all the relevant bits
                    .find('input, textarea, select, label')
                    .each(function () {
                        updateElementIndex(this, prefix, formCount);
                        var element = $(this);
                        if (element.is('select')) {
                            if (element.attr('id').indexOf('interval') >= 0) {
                                element.find('option:first').attr('selected', 'selected');
                            }
                        } else {
                            element.val('');
                        }
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
 * Update Calendar Ownership Reassignment url value in modal;
 * enable/disable submit button
 **/
var calendarSubscribeModal = function() {
    if ($('#calendar-subscribe-modal')) {
        var modal = $('#calendar-subscribe-modal');
        var submitBtn = modal.find('.modal-footer a.btn:first-child');

        $('.calendar-subscribe').click(function(e) {
            e.preventDefault();
            modal.modal('show');
        });

        submitBtn.click(function() {
            var newSubscriber = $('#new-subscription-select').val(),
                url = submitBtn.attr('href');
            if (newSubscriber !== '') {
                /* TODO: Fix stupid 'unrecognized expression' syntax error */
                url = url.replace(/calendar\/[A-Za-z0-9-]+\/subscribe/, 'calendar/' + newSubscriber + '/subscribe');
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
            var dropdown = $(this),
                autocompleteId = dropdown.attr('id') + '-autocomplete',
                locationCloneParent = dropdown.parents('.cloneable'),
                cloneBtn = locationCloneParent.parents('.control-group').find('.cloner'),
                locationRow = dropdown.parent('.location-search').parent('.row'),
                locationTitleSpan = locationRow.find('.location-selected-title'),
                locationRoomSpan = locationRow.find('.location-selected-room'),
                locationUrlSpan = locationRow.find('.location-selected-url'),
                locationNewForm = locationRow.find('.location-new-form');

            // Hide dropdown
            dropdown.hide();

            /**
             * Hide new location form if creating a new event instance
             * by checking whether the title field is empty. Display
             * location form if there something is in the title field.
             **/
            if (!locationNewForm.children('input[name*="-new_location_title"]').val()) {
                locationNewForm.hide();
            }

            // Add content to cloner btn
            cloneBtn.html('<div>Add another event instance...</div><a class="btn btn-success" href="#" alt="Add another event instance" title="Add another event instance"><i class="icon-plus"></i></a>');

            // Create search as you type field + other elements, if necessary
            var locationAutocomplete = null,
                locationNewBtn = null,
                suggestionList = null,
                locationRemoveBtn = null;

            if (dropdown.siblings('.location-autocomplete').length < 1) {
                locationAutocomplete = $('<input type="text" id="'+ autocompleteId +'" class="location-autocomplete search-query" autocomplete="off" placeholder="Type a location name..." />');
                locationAutocomplete.insertAfter(dropdown);

                locationNewBtn = $('<a class="location-new-btn btn btn-success" href="#" alt="Create New Location"><i class="icon-plus"></i></a>');
                locationNewBtn.insertAfter(locationAutocomplete).hide();

                suggestionList = $('<ul class="dropdown-menu location-suggestions"></ul>');
                suggestionList.insertAfter(locationNewBtn).hide();

                locationRemoveBtn = $('<a class="location-selected-remove" href="#" alt="Remove Location" title="Remove Location">&times;</a>');
                locationRemoveBtn.insertBefore(locationTitleSpan);
            }
            else {
                locationAutocomplete = dropdown.siblings('.location-autocomplete');
                locationNewBtn = dropdown.siblings('.location-new-btn');
                suggestionList = dropdown.siblings('.location-suggestions');
                locationRemoveBtn = locationRow.find('.location-selected-remove');
            }

            // Reassign dropdown label to autocomplete field
            dropdown.siblings('label[for*="-location"]').attr('for', autocompleteId);

            // Hide location remove btn if necessary
            if (dropdown.val() == '' && $.trim(locationTitleSpan.text()) == '') {
                locationRemoveBtn.hide();
            }

            // Perform a search + show suggestion list
            var autocompleteSearch = function(query) {
                var matchesFound = false;
                var matches = [];

                $.each(eventLocations, function(location, locationVals) {
                    if (location.toLowerCase().indexOf(query.toLowerCase()) > -1) {
                        // Push comboname to autocomplete suggestions list
                        matchesFound = true;
                        var listItem = $('<li data-location-id="' + locationVals.id + '" data-location-title="' + locationVals.title + '" data-location-room="' + locationVals.room + '" data-location-url="' + locationVals.url + '"></li>');
                        var link = $('<a tabindex="0" class="suggestion-link" href="#">' + location + '</a>');

                        // Assign click event to link
                        link.on('click', function(event) {
                            event.preventDefault();
                            selectSuggestion(listItem);
                        });

                        listItem.html(link);
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
                else {
                    suggestionList.hide();
                    // Show the 'create new location' button
                    locationNewBtn.show();
                }
            }

            // Prevent form submission via enter keypress in any autocomplete field
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
                //var query = locationAutocomplete.val().replace(/\W/g, '');
                var query = locationAutocomplete.val().replace(/([^a-zA-Z0-9\s-!$#%&+|:?])/g, '');

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
                            var selected = suggestionList.children('.selected');
                            var newselected = null;
                            if (event.keyCode == 40) {
                                // Move down one list item. Check if a list item is highlighted yet or not
                                if (selected.length > 0) {
                                    newselected = (selected.next('li').length !== 0) ? selected.next('li') : suggestionList.children('li').first();
                                }
                                else {
                                    newselected = suggestionList.children('li').first();
                                }
                            }
                            else if (event.keyCode == 38) {
                                // Move up one list item
                                if (selected.length > 0) {
                                    newselected = (selected.prev('li').length !== 0) ? selected.prev('li') : suggestionList.children('li').last();
                                }
                                else {
                                    newselected = suggestionList.children('li').last();
                                }
                            }
                            else if (event.keyCode == 39 || event.keyCode == 37) {
                                // Left/right key press; do nothing
                                return;
                            }
                            selected.removeClass('selected');
                            newselected.addClass('selected');
                            locationAutocomplete.val(newselected.attr('data-location-title'));
                        }
                    }
                    // If user hit enter on the autocomplete field, select the query
                    else if (event.type == 'keyup' && event.keyCode == 13) {
                        // We can only select existing locations that are currently highlighted
                        if (suggestionList.children().length > 0) {
                            var selected = suggestionList.children('.selected');
                            if (selected.length < 1) {
                                selectSuggestion(suggestionList.children('li').first());
                            }
                            else {
                                selectSuggestion(selected.first());
                            }
                        }
                        // Try to create a new location if no suggestions are found
                        else {
                            createNewLocation();
                        }
                    }
                }
                // Remove suggestion list if user emptied the field
                else {
                    suggestionList.empty().hide();
                }
            });

            var selectSuggestion = function(listItem) {
                // Remove any existing set location value
                unselectSuggestion();
                removeNewLocation(locationRemoveBtn);

                // Display new values to the user
                locationTitleSpan.text(listItem.attr('data-location-title')).show();
                locationRoomSpan.text(listItem.attr('data-location-room')).show();
                locationUrlSpan.html('<a href="' + listItem.attr('data-location-url') + '"><i class="icon-external-link"></i> ' + listItem.attr('data-location-url') + '</a>').show();

                // Hide autocomplete suggestions
                suggestionList.empty().hide();

                // Assign the hidden dropdown's value
                dropdown
                    .children('option[selected="selected"]')
                        .attr('selected', false)
                        .end()
                    .children('option[value="' + listItem.attr('data-location-id') + '"]')
                        .attr('selected', true);
                dropdown.get(0).selectedIndex = dropdown.children('option[value="' + listItem.attr('data-location-id') + '"]').val();

                // Show the location delete btn
                locationRemoveBtn.show();

                // Empty the current autocomplete field value
                locationAutocomplete.val('');
            };

            var unselectSuggestion = function() {
                //$(locationTitleSpan, locationRoomSpan, locationUrlSpan).text('').hide();
                locationTitleSpan.text('').hide();
                locationRoomSpan.text('').hide();
                locationUrlSpan.text('').hide();
                dropdown
                    .children('option[selected="selected"]')
                        .attr('selected', false)
                        .end()
                    .children('option[value=""]')
                        .attr('selected', true);
                locationRemoveBtn.hide();
            };

            var createNewLocation = function() {
                // Remove any existing set location value
                unselectSuggestion();
                removeNewLocation();

                // Show New Location form fields; populate Name field w/autocomplete field val
                locationNewForm
                    .show()
                    .children('input[name*="-new_location_title"]')
                        .val(locationAutocomplete.val());

                // Show location delete btn
                locationRemoveBtn.show();

                // Hide stuff we don't need
                suggestionList.empty().hide();
                locationNewBtn.hide();

                // Empty autocomplete field val
                locationAutocomplete.val('');
            }

            var removeNewLocation = function() {
                locationNewForm
                    .hide()
                    .children('input')
                        .val('');
                locationRemoveBtn.hide();
            }

            // Handle removal of a selected suggestion
            locationRemoveBtn.on('click', function(event) {
                event.preventDefault();
                unselectSuggestion();
                removeNewLocation();
            });

            // Handle new location creation
            locationNewBtn.on('click', function(event) {
                event.preventDefault();
                createNewLocation();
            });

            // Stupid selectedIndex fix for cloned location values
            if (locationCloneParent.hasClass('clone')) {
                dropdown.get(0).selectedIndex = dropdown.children('option[selected="selected"]').val();
            }
        });
    }
};

/**
 * Search for and add tags to an event
 **/
eventTagging = function() {
    if ($('#id_event-tags').length > 0) {
        var taglist = $('#id_event-tags');

        // Hide existing taglist
        taglist.hide();

        // Make sure all values in taglist field are enclosed in quotes
        var existingTaglistVal = taglist.val();
        if (existingTaglistVal !== '') {
            var vals = existingTaglistVal.split(',');
            for (var i = 0; i < vals.length; i++) {
                vals[i] = vals[i].trim();
                if (vals[i].charAt(0) !== '"') {
                    vals[i] = '"' + vals[i] + '"';
                }
            }
            vals = vals.join(',');
            // rejoin
            taglist
                .val(vals)
                .attr('value', vals);
        }

        // Update helptext
        var helpText = taglist.siblings('.help-text');
        helpText.text('Type a word or phrase, then hit the "enter" key or type a comma to add it to your list of tags.');

        // Create a new textfield for autocompletion
        var tagAutocomplete = $('<input type="text" id="id_event-tags-autocomplete" autocomplete="off" placeholder="Type a tag or phrase..." />');
        var suggestionList = $('<ul class="dropdown-menu" id="id_event-tags-suggestions"></ul>');
        var selectedTags = $('#event-tags-selected');
        tagAutocomplete.insertAfter(taglist);
        suggestionList.insertAfter(helpText);

        // Handle a form validation error, where new tags are saved in
        // the hidden taglist field but are not yet saved + populated
        // in the selectedTags list
        if (taglist.val() !== '' && selectedTags.children().length < 1) {
            // Strip wrapper quotes, separate by comma and remove empty vals
            var tagArray = taglist.val().replace(/\"/g, '').split(',').filter(Boolean);
            $.each(tagArray, function(key, val) {
                selectedTags
                    .append('<li data-tag-name="'+ val +'"><a href="#" class="selected-remove" alt="Remove this tag">&times;</a>'+ val +'</li>')
            });
        }

        // Perform a search + show suggestion list
        var autocompleteSearch = function(query) {
            var matchesFound = false;
            var matches = [];

            for (var i = 0; i < eventTags.length; i++) {
                var tagName = eventTags[i];
                if (tagName.toLowerCase().indexOf(query.toLowerCase()) > -1) {
                    // Push comboname to autocomplete suggestions list
                    matchesFound = true;
                    var listItem = $('<li data-tag-name="' + tagName + '"></li>');
                    var link = $('<a tabindex="0" class="suggestion-link" href="#">' + tagName + '</a>');

                    // Assign click event to link
                    link.on('click', function(event) {
                        event.preventDefault();
                        addTag($(this).parent('li'));
                    });

                    listItem.html(link);
                    matches.push(listItem);
                }
            }
            if (matchesFound == true) {
                // Append matches to list
                $.each(matches, function(index, val) {
                    val.appendTo(suggestionList);
                });
                suggestionList.show();
            }
            else {
                suggestionList.hide();
            }
        }

        // Prevent form submission via enter keypress in any autocomplete field
        taglist.parents('form').on('submit', function(event) {
            if (tagAutocomplete.is(':focus')) {
                return false;
            }
        });

        // Handle typing into search field
        var timer = null;
        var delay = 300;

        tagAutocomplete.on('keyup focus', function(event) {
            clearTimeout(timer);
            var query = tagAutocomplete.val().replace(/([^a-zA-Z0-9\s-!$#%&+|:?])/g, '');

            // Execute a search for a non-empty field val.
            // Searches eventLocations object (created in template.)
            if (query !== '') {
                // Detect standard alphanumeric chars (and onfocus event)
                if (
                    (event.type == 'focus') ||
                    (event.type == 'keyup' && event.keyCode !== 8 && event.keyCode > 44 && event.keyCode !== 188)
                ) {
                    timer = setTimeout(function() {
                        suggestionList.empty();
                        autocompleteSearch(query);
                    }, delay);
                }
                // If user typed a non-alphanumeric key, check for up/down strokes
                else if (event.type == 'keyup' && event.keyCode > 36 && event.keyCode < 41) {
                    if (suggestionList.children().length > 0) {
                        var selected = suggestionList.children('.selected');
                        var newselected = null;
                        if (event.keyCode == 40) {
                            // Move down one list item. Check if a list item is highlighted yet or not
                            if (selected.length > 0) {
                                newselected = (selected.next('li').length !== 0) ? selected.next('li') : suggestionList.children('li').first();
                            }
                            else {
                                newselected = suggestionList.children('li').first();
                            }
                        }
                        else if (event.keyCode == 38) {
                            // Move up one list item
                            if (selected.length > 0) {
                                newselected = (selected.prev('li').length !== 0) ? selected.prev('li') : suggestionList.children('li').last();
                            }
                            else {
                                newselected = suggestionList.children('li').last();
                            }
                        }
                        else if (event.keyCode == 39 || event.keyCode == 37) {
                            // Left/right key press; do nothing
                            return;
                        }
                        selected.removeClass('selected');
                        newselected.addClass('selected');
                        tagAutocomplete.val(newselected.attr('data-tag-name'));
                    }
                }
                // If user hit enter or comma on the autocomplete field, select the query
                else if (event.type == 'keyup' && (event.keyCode == 13 || event.keyCode == 188)) {
                    // Add the tag to the tag list.  Taggit handles creation of new
                    // or assignment of existing tags
                    addTag($('<li data-tag-name="'+ query +'"><a tabindex="0" class="suggestion-link" href="#">'+ query +'</a></li>'));
                }
            }
            // Remove suggestion list if user emptied the field
            else {
                suggestionList.empty().hide();
            }
        });

        var addTag = function(listItem) {
            var removeLink = $('<a href="#" class="selected-remove" alt="Remove this tag" title="Remove this tag">&times;</a>');
            removeLink.on('click', function(event) {
                event.preventDefault();
                removeTag($(this).parent('li'));
            });

            var tagName = listItem.attr('data-tag-name');

            // Display new values to the user
            listItem.appendTo(selectedTags).prepend(removeLink);

            // Hide autocomplete suggestions
            suggestionList.empty().hide();

            // Remove original suggestion link
            listItem.find('.suggestion-link').replaceWith(tagName);

            // Assign the hidden textfield's value
            taglist.val(taglist.val() + '"' + tagName + '",');

            // Empty the current autocomplete field value
            tagAutocomplete.val('');
        };

        var removeTag = function(listItem) {
            // Remove selected list item
            selectedTags.find(listItem).remove();

            // Remove from hidden textfield's value. Check for stray comma + remove if necessary
            var newval = '';
            if (taglist.val().indexOf('"' + listItem.attr('data-tag-name') + '",') > -1) {
                newval = taglist.val().replace('"' + listItem.attr('data-tag-name') + '",', '');
            }
            else {
                newval = taglist.val().replace('"' + listItem.attr('data-tag-name') + '"', '');
            }
            taglist
                .val(newval)
                .attr(newval);
        }

        $('.selected-remove').on('click', function(event) {
            event.preventDefault();
            removeTag($(this).parent('li'));
        });
    }
};

/**
 * Toggle 'demote' modal
 **/
var toggleModalUserDemote = function() {
    var modal = $('#user-demote-modal');

    $('.demote-self').click(function(e) {
        e.preventDefault();

        var userName  = $(this).attr('data-user-name'),
            demoteURL = $(this).attr('href');

        /* Insert user name in modal text */
        modal
            .find('h2 span.alt')
                .text(userName)
                .end()
            .find('.modal-footer a.btn-danger')
                .attr('href', demoteURL)
                .end()
            .modal('show');
    });

    var submitBtn = modal.find('.modal-footer a.btn:first-child');
    submitBtn.click(function() {
        var newObject = $('#new-object-select').val(),
            url = submitBtn.attr('href');
        if (newObject !== '') {
            url = url.replace(/merge\/[A-Za-z0-9]+$/, 'merge/' + newObject);
            submitBtn.attr('href', url);
        }
    });
};

/**
 * Update frontend calendar month view month/year form
 * "action" value on dropdown change
 **/
var updateMonthviewDropdown = function() {
    var form = $('#month-toggle'),
        yearSelect = form.find('#id_year'),
        monthSelect = form.find('#id_month');
    monthSelect.change(function() {
        var action = form.attr('action'),
            newMonth = '/' + $(this).val() + '/',
            oldMonth = action.slice((action.length - 4), action.length),
            newAction = action.replace(oldMonth, newMonth);
        form.attr('action', newAction);
    });
    yearSelect.change(function() {
        var action = form.attr('action'),
            newYear = '/' + $(this).val() + '/',
            oldYear = action.slice((action.length - 9), (action.length - 3)),
            newAction = action.replace(oldYear, newYear);
        form.attr('action', newAction);
    });
};

/**
 * Sets the event contact information to the current user.
 **/
 var eventContactInfo = function() {
    $('#add-user-contact-info').click(function(event) {
        var button = $(this);
        event.preventDefault();
        if (usersFullName && usersEmail) {
            $('#id_event-contact_name').val(usersFullName);
            $('#id_event-contact_email').val(usersEmail);
        }
    });
 }



$(document).ready(function() {
    bulkSelectAll();
    bulkActionSubmit();
    autoOpenTagByAnchor();
    toggleModalModifyObject();
    toggleModalMergeObject();
    toggleModalUserDemote();
    calendarSliders();
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
    calendarSubscribeModal();
    toggleEventListRecurrences();
    eventLocationsSearch($('select.location-dropdown'));
    eventTagging();
    updateMonthviewDropdown();
    eventContactInfo();
});
