/* global eventLocations, eventTags, usersFullName, usersEmail, EARLIEST_VALID_DATE, LATEST_VALID_DATE */

/* Scripts listed below should only need to be executed on the site backend (manager views.) */


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
        var bulkForm = this.form,
            actionInput = $(this),
            actionInputValue = actionInput.find('option:selected'),
            eventsSelected = $('input:checkbox:checked[name="object_ids"]'),
            recurringEvents = false;

        if (!actionInputValue.attr('value') || actionInputValue.attr('value') === 'empty' || !eventsSelected.length) {
            // Don't do anything if there isn't a value
            return;
        } else if (actionInputValue.val() === 'delete') {
            eventsSelected.each(function() {
                var checkbox = $(this);

                if (parseInt(checkbox.attr('data-event-instance-count')) > 1) {
                    recurringEvents = true;
                    return false;
                }
            });

            if (recurringEvents) {
                var bulkEventDeleteModal = $('#bulk-event-delete-modal');
                bulkEventDeleteModal.find('#bulk-event-delete-btn').click(function() {
                    bulkForm.submit();
                });
                bulkEventDeleteModal.modal();
            } else {
                bulkForm.submit();
            }
        } else {
            bulkForm.submit();
        }
    });
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
 * Toggle 'Merge Tag/Category' modal
 **/
var toggleModalMergeObject = function() {
    var modal = $('#object-merge-modal');

    $('.category-merge, .tag-merge, .location-merge').click(function(e) {
        e.preventDefault();

        var objectTitle = $(this).attr('data-object-title'),
            objectPk    = $(this).attr('data-object-pk'),
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
                    if ($(this).text() === objectTitle && $(this).val() === objectPk) {
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
 * Toggle Calendar user 'demote' modal
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
 * Date/Timepicker Init.
 * Use Bootstrap datepicker/jQuery timepicker plugins.
 **/
var fallbackDtpOnClick = function(icon) {
    var input = icon.siblings('input');
    if (!input.is(':focus')) {
        input.focus();
    }
};
var initiateDatePickers = function(fields) {
    fields
        .each(function() {
            var field = $(this);

            // Wrap field in wrapper div; add icon
            if (field.parent().hasClass('bootstrap-datepicker') === false) {
                field
                    .addClass('form-control')
                    .wrap('<div class="bootstrap-dtp bootstrap-datepicker" />')
                    .parent()
                        .append('<i class="fa fa-calendar" />');
            }

            var fieldParent = field.parent().parent();
            var siblingDateField = fieldParent.siblings().find('.' + field.attr('class'));

            field
                .datepicker({
                    format: 'mm/dd/yyyy',
                    autoclose: true,
                    todayHighlight: true,
                    startDate: EARLIEST_VALID_DATE,
                    endDate: LATEST_VALID_DATE
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

            // Assign click event to icon
            fieldParent
                .find('i')
                    .on('click', function() { fallbackDtpOnClick($(this)); });
        })
        .removeClass('placeholder') // placeholder plugin checks if this class exists on the field and won't reinitiate if it does.
        .placeholder(); // Force init placeholder for old browsers

};
var initiateTimePickers = function(fields) {
    fields
        .each(function(){
            var field = $(this);

            // Wrap each timepicker input if this field isn't a clone
            if (field.parent().hasClass('bootstrap-timepicker') === false) {
                field
                    .addClass('form-control')
                    .wrap('<div class="bootstrap-dtp bootstrap-timepicker" />')
                    .parent()
                        .append('<i class="fa fa-clock-o" />');
            }

            var fieldParent = field.parent().parent();

            // Assign click event to icon
            fieldParent
                .find('i')
                    .on('click', function() { fallbackDtpOnClick($(this)); });
        })
        .timepicker({
            'scrollDefaultNow': true,
            'timeFormat': 'h:i A',
            'step': 15
        })
        .removeClass('placeholder') // placeholder plugin checks if this class exists on the field and won't reinitiate if it does.
        .placeholder(); // Force init placeholder for old browsers
};

/**
 * Adds copied rereview data to their respective fields on the
 * Event Update view.
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
 * Generic autocomplete class that searches string values from an existing
 * <select> field, or other data, and updates that field as suggestions are found.
 * Methods can be overridden before calling init to customize data parsing.
 **/
var selectFieldAutocomplete = function(autocompleteField, dataField) {
    this.autocompleteField = autocompleteField; // jQuery object of the <input> field to perform autocomplete on
    this.dataField = dataField;                 // jQuery object of the <select> field of options to search against and submit when the form is submitted.
    this.form = dataField.parents('form');      // The autocomplete <form>
    this.searchableTerms = [];                  // Array used by Bootstrap typeahead to search queries against. Should contain only strings.
    this.mappedData = {};                       // Complete objects that represent searchable data
    this.selection = null;                      // The current selected autocomplete value

    // Function that performs pre-search setup; i.e. shows/hides various fields.
    this.setupForm = function() {
        return;
    };

    // Prevent form submission via enter keypress in autocomplete field
    this.onFormSubmission = function() {
        var self = this;
        self.form.on('submit', function() {
            if (self.autocompleteField.is(':focus')) {
                return false;
            }
        });
    };

    // Clear hidden field value if autocomplete field is cleared.
    this.checkEmptyValues = function() {
        var self = this;
        self.autocompleteField.on('keydown', function(event) {
            if (!self.autocompleteField.val() && (event.type === 'keydown' && (event.keyCode === 8 || event.keyCode === 46))) {
                self.autocompleteField.trigger('change');
                if (self.dataField.is('select')) {
                    self.dataField.children('option:selected').removeAttr('selected');
                    self.dataField.children('option:selected').prop('selected', false);
                }
                self.dataField.val('');
            }
        });
    };

    // Set searchableTerms array and mappedData values.
    // Must be overridden if dataField is not a <select> field.
    this.setSearchTerms = function() {
        var self = this;
        if (self.dataField.is('select')) {
            $.each(self.dataField.children('option:not([disabled])'), function() {
                var option = $(this),
                    key = option.val(),
                    val = option.text();
                if ($.trim(val).length < 1) {
                    val = key + ' (name n/a)';
                }

                self.mappedData[val] = key;
                self.searchableTerms.push(val);
            });
        }
    };

    // Function to pass to Bootstrap Typeahead's 'source' method.
    this.typeaheadSource = function(query, process) {
        var self = this;
        return process(self.searchableTerms);
    };

    // Function to pass to Bootstrap Typeahead's 'matcher' method.
    this.typeaheadMatcher = function(item, query) {
        if (item.toLowerCase().indexOf(query.trim().toLowerCase()) !== -1) {
            return true;
        }
    };

    // Function to pass to Bootstrap Typeahead's 'updater' method.
    // This function must return 'item' to keep autocompleteField populated.
    this.typeaheadUpdater = function(item) {
        var self = this;
        self.selection = self.mappedData[item];
        self.dataField.val(self.selection);
        if (self.dataField.is('select')) {
            self.dataField
                .children('option[value="'+ self.selection +'"]')
                    .attr('selected', true)
                    .prop('selected', true);
        }
        return item;
    };

    this.init = function() {
        var self = this;
        self.setupForm();
        self.onFormSubmission();
        self.checkEmptyValues();
        self.setSearchTerms();

        self.autocompleteField.typeahead({
            items: 10,
            minLength: 2,
            source: function(query, process) {
                self.typeaheadSource(query, process);
            },
            matcher: function(item) {
                var query = this.query;
                return self.typeaheadMatcher(item, query);
            },
            updater: function(item) {
                item = self.typeaheadUpdater(item);
                return item;
            }
        });
    };
};


/**
 * User search typeahead + form validation
 **/
var userSearchTypeahead = function() {
    var autocompleteField = $('#id_add_user'),
        usersField = $('#id_username_d'),
        roleField = $('#id_role'),
        form = usersField.parents('form'),
        addBtn = form.find('button');

    // Initiate autocomplete form
    var autocomplete = new selectFieldAutocomplete(autocompleteField, usersField);
    autocomplete.roleField = roleField;
    autocomplete.addBtn = addBtn;

    autocomplete.setupForm = function() {
        var self = this;

        // Enable autocomplete field. Hide data field.
        self.dataField.hide();
        self.autocompleteField.show();
        $('label[for="'+ self.dataField.attr('id') +'"]').attr('for', self.autocompleteField.attr('id'));

        // Handle form validation (don't allow new users to be submitted w/o valid name, role)
        var handler = function(e) {
            e.preventDefault();
        };
        var toggleAddBtn = function() {
            if (
                self.autocompleteField.val() === '' ||
                !self.dataField.val() ||
                self.roleField.val() === '' ||
                self.autocompleteField.val() === self.autocompleteField.attr('placeholder')
            ){
                self.addBtn
                    .addClass('disabled')
                    .bind('click', handler);
            }
            else {
                var selected = self.dataField.children('option').selected || self.dataField.children('option[selected="selected"]');
                if (typeof selected !== 'undefined' && selected.length > 0 && selected.text() === self.autocompleteField.val()) {
                    self.addBtn
                        .removeClass('disabled')
                        .unbind('click', handler);
                }
                else {
                    self.addBtn
                        .addClass('disabled')
                        .bind('click', handler);
                }

            }
        };
        toggleAddBtn();
        $([self.autocompleteField, self.dataField, self.roleField]).each(function() {
            $(this).on('change', function() {
                toggleAddBtn();
            });
        });
    };
    autocomplete.onFormSubmission = function() {
        var self = this;
        self.form.on('submit', function() {
            if (self.autocompleteField.is(':focus')) {
                return false;
            }
            else if (self.form.find('button').hasClass('disabled') === false) {
                var url = self.form.attr('action'),
                    username = self.dataField.children('option:selected').val(),
                    role = self.roleField.val();
                url = url.replace('/username/role', '/' + username + '/' + role);
                self.form.attr('action', url);
            }
        });
    };
    autocomplete.init();
};


/**
 * Create/Update Event location searching + creation
 * Arg: $('select.location-dropdown')
 **/
var eventLocationsSearch = function(locationDropdowns) {
    if (locationDropdowns.length > 0) {
        locationDropdowns.each(function() {
            var locationsField = $(this), // 'dropdown'
                autocompleteId = locationsField.attr('id') + '-autocomplete',
                autocompleteField = $('<input type="text" id="'+ autocompleteId +'" class="form-control location-autocomplete search-query" autocomplete="off" placeholder="Type a location name..." />'),
                locationRow = locationsField.parent('.location-search').parent('.row'),
                locationTitleSpan = locationRow.find('.location-selected-title'),
                locationRoomSpan = locationRow.find('.location-selected-room'),
                locationUrlSpan = locationRow.find('.location-selected-url'),
                newLocationForm = locationRow.find('.location-new-form');

            var autocomplete = new selectFieldAutocomplete(autocompleteField, locationsField);

            autocomplete.addBtn = $('<a class="autocomplete-new-btn btn btn-success" href="#" alt="Create New Location"><i class="fa fa-plus"></i></a>');
            autocomplete.removeBtn = $('<a class="location-selected-remove" href="#" alt="Remove Location" title="Remove Location">&times;</a>');
            autocomplete.locationRow = locationRow;
            autocomplete.locationTitleSpan = locationTitleSpan;
            autocomplete.locationRoomSpan = locationRoomSpan;
            autocomplete.locationUrlSpan = locationUrlSpan;
            autocomplete.newLocationForm = newLocationForm;

            // Custom function that displays the New Location form fields
            // and populates it with the location name typed in the autocomplete field.
            autocomplete.createNewLocation = function(item) {
                var self = this;

                // Remove any existing set location value
                self.removeLocation();

                // Show New Location form fields; populate Name field w/autocomplete field val
                self.newLocationForm
                    .show()
                    .children('input[name*="-new_location_title"]')
                        .val(item);

                self.removeBtn.show();
                self.addBtn.hide();
                self.autocompleteField.val('');
            };

            // Custom function for removing selected location data.
            // This function updates self.dataField's value.
            autocomplete.removeLocation = function() {
                var self = this;

                // Clear previously selected data displayed to user
                self.locationTitleSpan.text('').hide();
                self.locationRoomSpan.text('').hide();
                self.locationUrlSpan.text('').hide();

                // Clear values previously set in new location form
                self.newLocationForm
                    .hide()
                    .children('input')
                        .val('');

                // Update self.dataField
                self.dataField
                    .children('option[selected="selected"]')
                        .removeAttr('selected')
                        .prop('selected', false);

                self.removeBtn.hide();
            };

            autocomplete.setupForm = function() {
                var self = this;

                // Destroy any existing dynamic form elements that were cloned.
                self.locationRow.find('.' + self.addBtn.attr('class')).remove();
                self.locationRow.find('.' + self.removeBtn.attr('class')).remove();
                self.locationRow.find('#' + self.autocompleteField.attr('id')).remove();

                // Enable autocomplete field. Hide data field.
                self.dataField.hide();
                self.autocompleteField
                    .insertAfter(self.dataField)
                    .show();
                $('label[for="'+ self.dataField.attr('id') +'"]').attr('for', self.autocompleteField.attr('id'));

                // Insert other dynamic form elements.
                self.addBtn
                    .insertAfter(self.autocompleteField)
                    .hide();
                self.removeBtn
                    .insertBefore(self.locationTitleSpan);

                // Hide new location form if creating a new event instance
                // by checking whether the title field is empty. Display
                // location form if there something is in the title field.
                if (!self.newLocationForm.children('input[name*="-new_location_title"]').val()) {
                    self.newLocationForm.hide();
                }

                // Hide removeBtn on load, if necessary
                var $unemptyNewLocationFormInputs = self.newLocationForm.find('input').filter(function() { return $.trim($(this).val()) !== ''; }),
                    contentInNewLocationForm = $unemptyNewLocationFormInputs.length === 0 ? false: true;

                if (
                  self.dataField.val() === '' &&
                  $.trim(self.locationTitleSpan.text()) === '' &&
                  !contentInNewLocationForm
                ) {
                    self.removeBtn.hide();
                }

                // Handle removal of a selected suggestion
                self.removeBtn.on('click', function(event) {
                    event.preventDefault();
                    self.removeLocation();
                });

                // Handle new location creation
                self.addBtn.on('click', function(event) {
                    event.preventDefault();
                    var item = self.autocompleteField.val();
                    self.createNewLocation(item);
                });
                self.autocompleteField.on('keydown focus', function(event) {
                    // TODO: better way of determining if a match has been found?
                    var typeaheadSuggestions = self.autocompleteField.siblings('.typeahead.dropdown-menu');
                    var matchFound = (typeaheadSuggestions.children('li').length > 0 && typeaheadSuggestions.is(':visible')) ? true : false;

                    // Show addBtn if no match is found and the user didn't type Enter or a comma.
                    if (self.autocompleteField.val() !== '') {
                        if (!matchFound && (event.type === 'keydown' && event.keyCode !== 13 && event.keyCode !== 188)) {
                            self.addBtn.show();
                        }
                        // Create a new location if the user didn't find a match,
                        // but entered either a comma or Enter
                        else if (
                            (!matchFound && (event.type === 'keydown' && event.keyCode === 13)) ||
                            (event.type === 'keydown' && event.keyCode === 188)
                        ) {
                            // Add the location data to the New Location form
                            var item = self.autocompleteField.val();
                            self.createNewLocation(item);
                            self.addBtn.hide();

                            // Don't allow form submission to pass!
                            return false;
                        }
                    }
                    // Make sure the addBtn is hidden otherwise.
                    else {
                        self.addBtn.hide();
                    }
                });
            };

            autocomplete.typeaheadUpdater = function(item) {
                var self = this;

                // Remove any existing selected location
                self.removeLocation();

                // Update current selection
                self.selection = self.mappedData[item];
                self.dataField
                    .val(self.selection)
                    .children('option[value="'+ self.selection +'"]')
                        .attr('selected', true)
                        .prop('selected', true);

                var selectedData = eventLocations[self.selection]; // eventLocations is defined in head of event create/update template

                // Display new values to the user
                if (selectedData.title !== 'None' && selectedData.title !== '') {
                    self.locationTitleSpan
                        .text(selectedData.title)
                        .show();
                }
                if (selectedData.room !== 'None' && selectedData.room !== '') {
                    self.locationRoomSpan
                        .text(selectedData.room)
                        .show();
                }
                if (selectedData.url !== 'None' && selectedData.url !== '') {
                    self.locationUrlSpan
                        .html('<a href="' + selectedData.url + '">' + selectedData.url + '</a>')
                        .show();
                }

                self.removeBtn.show();
                self.addBtn.hide();

                return '';
            };

            autocomplete.init();
        });
    }
};


/**
 * Search for and add tags to an event.
 * Hidden data field value is updated with tag selections on form submit.
 **/
var eventTagging = function() {
    var autocompleteField = $('<input type="text" class="form-control" id="id_event-tags-autocomplete" autocomplete="off" placeholder="Type a tag or phrase..." />'),
        tagsField = $('#id_event-tags'),
        addBtn = $('<a class="autocomplete-new-btn btn btn-success" href="#" alt="Create New Tag"><i class="fa fa-plus"></i></a>'),
        selectedTagsList = $('#event-tags-selected');

    if (tagsField.length > 0) {
        // Initiate autocomplete form
        var autocomplete = new selectFieldAutocomplete(autocompleteField, tagsField);

        autocomplete.addBtn = addBtn;
        autocomplete.selectedTagsList = selectedTagsList;
        // Create an array of chosen tags to add to the event on form submit
        autocomplete.selectedTagsArray = [];

        // Custom function for populating self.selectedTagList with list items.
        // To be used by self.typeaheadUpdater and when populating self.selectedTagList with
        // existing self.dataField values.
        // This function does NOT update self.dataField's value.
        autocomplete.createTag = function(item) {
            var self = this;
            var removeLink = $('<a href="#" class="selected-remove" alt="Remove this tag" title="Remove this tag">&times;</a>');
            removeLink.on('click', function(event) {
                event.preventDefault();
                self.removeTag($(this).parent('li'));
            });

            // Make sure that item is still some valid value after cleaning and trimming whitespace
            if (item.length > 0) {
                var tagListItem = $('<li data-tag-name="'+ item +'">'+ item +'</li>');
                tagListItem
                    .appendTo(self.selectedTagsList)
                    .prepend(removeLink);

                self.addBtn.hide();
            }
            else {
                return false;
            }
        };

        // Custom function for removing selected tag list items.
        // This function DOES update self.selectedTagsArray.
        autocomplete.removeTag = function(listItem) {
            var self = this;
            self.selectedTagsList
                .find(listItem)
                .remove();

            var item = listItem.attr('data-tag-name');
            self.selectedTagsArray.splice($.inArray(item, self.selectedTagsArray), 1);
        };

        // Custom function that returns a 'clean' string value, after running through
        // a regular expression to only allow whitelisted characters below
        autocomplete.getCleanItemVal = function(item) {
            return $.trim(item.replace(/([^a-zA-Z0-9\s-!$#%&+|:?])/g, ''));
        };

        autocomplete.setupForm = function() {
            var self = this;
            if (self.dataField.is(':visible')) {
                // Get existing tags from self.dataField and push them to self.selectedTagsArray.
                // Populate the selectedTagsList with existing tags.
                var existingTaglistVal = '';
                if (self.dataField.val()) {
                    existingTaglistVal = self.dataField.val();
                }
                else if (self.dataField.attr('value')) {
                    existingTaglistVal = self.dataField.attr('value');
                }
                if (existingTaglistVal !== '') {
                    // Create array from existingTaglistVal. $.grep removes empty results.
                    var tagArray = $.grep(existingTaglistVal.replace(/(&quot;?)|\"/g, '').split(','), function(val) { return val !== ''; });
                    self.selectedTagsArray = self.selectedTagsArray.concat(tagArray);

                    if (self.selectedTagsList.children().length < 1) {
                        $.each(tagArray, function(key, val) {
                            self.createTag(self.getCleanItemVal(val));
                        });
                    }
                }

                // Enable autocomplete field. Hide data field.
                self.dataField.hide();
                self.autocompleteField
                    .insertAfter(self.dataField)
                    .show();
                $('label[for="'+ self.dataField.attr('id') +'"]').attr('for', self.autocompleteField.attr('id'));

                // Insert "Add Tag" btn onto page
                self.addBtn
                    .insertAfter(self.autocompleteField)
                    .hide();

                // Update help text
                var helpText = self.dataField.siblings('.help-block');
                helpText.text('Type a word or phrase, then hit the "enter" key or type a comma to add it to your list of tags.');
            }

            // Handle addBtn clicks
            self.addBtn.on('click', function(event) {
                event.preventDefault();
                var item = self.getCleanItemVal(self.autocompleteField.val());
                if (item.length > 0) {
                    self.typeaheadUpdater(item);
                }
            });

            // Handle non-suggestion new tag creation
            self.autocompleteField.on('keydown focus', function(event) {
                // TODO: better way of determining if a match has been found?
                var typeaheadSuggestions = self.autocompleteField.siblings('.typeahead.dropdown-menu');
                var matchFound = (typeaheadSuggestions.children('li').length > 0 && typeaheadSuggestions.is(':visible')) ? true : false;

                // Show addBtn if no match is found and the user didn't type Enter or a comma.
                if (self.autocompleteField.val() !== '') {
                    if (!matchFound && (event.type === 'keydown' && event.keyCode !== 13 && event.keyCode !== 188)) {
                        self.addBtn.show();
                    }
                    // Create a new tag if the user didn't find a match,
                    // but entered either a comma or Enter
                    else if (
                        (!matchFound && (event.type === 'keydown' && event.keyCode === 13)) ||
                        (event.type === 'keydown' && event.keyCode === 188)
                    ) {
                        // Add the tag to the tag list.  Taggit handles creation of new
                        // or assignment of existing tags
                        var item = self.getCleanItemVal(autocompleteField.val());
                        if (item.length > 0) {
                            self.typeaheadUpdater(item);
                        }
                        self.addBtn.hide();

                        // Don't allow form submission to pass!
                        return false;
                    }
                }
                // Make sure the addBtn is hidden otherwise.
                else {
                    self.addBtn.hide();
                }
            });
        };

        autocomplete.onFormSubmission = function() {
            var self = this;
            self.form.on('submit', function() {
                if (self.autocompleteField.is(':focus')) {
                    return false;
                }
                else {
                    if (self.autocompleteField.val() !== '' && self.autocompleteField.val() !== self.autocompleteField.attr('placeholder')) {
                        self.selectedTagsArray.push(self.autocompleteField.val());
                    }
                    // Push the final value of selectedTagsArray to dataField's value. Add comma to
                    // the end of the string to force comma-based delimiting for Taggit.
                    var selectedTagsStr = self.selectedTagsArray.toString() + ',';
                    self.dataField
                        .val(selectedTagsStr)
                        .attr('value', selectedTagsStr);
                }
            });
        };

        autocomplete.setSearchTerms = function() {
            var self = this;
            // eventTags is defined in manager/events/create_update.html
            self.searchableTerms = eventTags;
            $.each(eventTags, function(key, val) {
                self.mappedData[val] = val;
            });
        };

        autocomplete.typeaheadUpdater = function(item) {
            var self = this;
            self.selection = self.mappedData[item];
            self.selectedTagsArray.push(item);
            self.autocompleteField.val('');
            self.createTag(item);
            return '';
        };

        autocomplete.init();
    }
};


/**
 * Clone fieldsets of the EventInstance formset of the Event Create/Update form.
 * Auto-increment field IDs as necessary.
 **/
function cloneableEventInstances() {
  var $form,                   // Not technically a form, but the <fieldset> that wraps the event instance forms
      formPrefix,              // Serves as a base for generating new event instance form prefixes
      $instanceTemplate,       // Reference to clean markup from which event instance form clones should be created
      instanceTemplateIndex,   // Some arbitrary string; gets appended to instanceTemplatePrefix
      instanceTemplatePrefix,  // Prefix for form field and input IDs, labels, and other attributes for $instanceTemplate
      $clonerBtn,              // Button that generates new clones when clicked
      $instanceTotal,          // Hidden input used by Django which stores the total number of instances in $form (that aren't deleted)
      instanceMaxVal;          // Grabbed from hidden input used by Django; the max number of instances that can be saved to an event

  /**
   * Updates IDs, labels, etc. as necessary for Event Instance formsets.
   * This function checks for form elements specific to Event Instances
   * (checkboxes, inputs, selects)--if new form elements are ever added to
   * the Event Instance formset, this function may need to be updated.
   **/
  function updateInstancePrefix($instance, oldPrefix, newPrefix) {

    // Update $instance's ID
    $instance.attr('id', newPrefix);

    var $prefixedElements = $instance.find('checkbox, input, select, label'),
        $removeBtn = $instance.find('.remove-instance'),
        regex = new RegExp(oldPrefix, 'gm');

    for (var i = 0; i < $prefixedElements.length; i++) {
      var $elem = $prefixedElements.eq(i),
          attrFor = $elem.attr('for'),
          attrID = $elem.attr('id'),
          attrName = $elem.attr('name');

      if (attrFor) {
        $elem.attr('for', attrFor.replace(regex, newPrefix));
      }
      if (attrID) {
        $elem.attr('id', attrID.replace(regex, newPrefix));
      }
      if (attrName) {
        $elem.attr('name', attrName.replace(regex, newPrefix));
      }
    }

    $removeBtn.attr('data-instance', '#' + newPrefix);

    return $instance;
  }

  /**
   * Clone $instanceTemplate and insert at the bottom of the
   * Event Instance form
   **/
  function addInstance() {
    var activeInstanceTotal = getActiveInstanceTotal();
    if (activeInstanceTotal < instanceMaxVal) {
      var $instance = $instanceTemplate.clone(false),
          $instances = $form.find('.event-instance'),
          newPrefix = formPrefix + '-' + $instances.length;

      $instance = updateInstancePrefix($instance, $instance.attr('id'), newPrefix);

      // Animate insertion into DOM
      // NOTE slideDown used here in lieu of CSS animations for IE8 support
      $instance
        .addClass('clone')
        .hide()
        .insertAfter($form.find('.event-instance:last'))
        .slideDown(300);

      setupInstanceEventHandlers($instance);

      incrementInstanceTotal();

      $form.trigger('formChanged');
    }
    else {
      window.alert('Sorry, an event cannot have more than ' + instanceMaxVal + ' unique event instances.');
    }
  }

  function clonerBtnClickHandler(e) {
    e.preventDefault();
    addInstance();
  }

  /**
   * Callback after an event instance is "removed"
   **/
  function updateInstancesPostRemoval() {

    var $removedInstance = $(this); // passed from slideUp() callback

    // If this instance was never saved to the backend (is a clone),
    // remove it from the DOM entirely.  Else, keep it in the DOM but
    // check the DELETE checkbox for the instance
    if ($removedInstance.hasClass('clone')) {
      $removedInstance.remove();

      var $instances = $form.find('.event-instance');

      // Go through all instances and update prefixes on clones, since
      // they may be out of order now
      for (var index = 0; index < $instances.length; index++) {
        var $theInstance = $instances.eq(index);

        // Only modify prefixes of clones (non-clones should never fall out of order)
        if ($theInstance.hasClass('clone')) {
          var newPrefix = formPrefix + '-' + index;
          updateInstancePrefix($theInstance, $theInstance.attr('id'), newPrefix);
          setupInstanceEventHandlers($theInstance);
        }
      }
    }
    else {
      $removedInstance
        .addClass('event-instance-removed')
        .find('#id_' + $removedInstance.attr('id') + '-DELETE')
          .prop('checked', true);
    }

    $form.trigger('formChanged');
  }

  /**
   * Hide the given Event Instance and mark it for removal
   * on form submit.  Update remaining Event Instance prefixes.
   **/
  function removeInstance($instance) {
    var activeInstanceTotal = getActiveInstanceTotal(),
        isClone = $instance.hasClass('clone');

    if (activeInstanceTotal > 1) {
      // Animate hiding from DOM; perform post-removal actions as needed.
      // NOTE slideUp used here in lieu of CSS animations for IE8 support
      $instance.slideUp(300, updateInstancesPostRemoval);

      // Only decrease the instance total if $instance is a clone--Django's
      // form validation requires non-clones marked as deletion to still be
      // counted toward the total number of instances.
      if (isClone) {
        decrementInstanceTotal();
      }
    }
  }

  function removeBtnClickHandler(e) {
    e.preventDefault();
    var $btn = $(e.target);
    removeInstance($form.find($btn.attr('data-instance')));
  }

  /**
   * Returns the number of .event-instance's in the form that are not marked
   * for deletion (instances that are "actively" visible).
   **/
  function getActiveInstanceTotal() {
    return $form.find('.event-instance:not(.event-instance-removed)').length;
  }

  /**
   * Increments $instanceTotal's value by 1.  This function should always
   * be called any time an instance is added to $form.
   **/
  function incrementInstanceTotal() {
    var oldInstanceTotalVal = parseInt($instanceTotal.val(), 10),
        newInstanceTotalVal = oldInstanceTotalVal + 1;

    $instanceTotal.val(newInstanceTotalVal);

    return newInstanceTotalVal;
  }

  /**
   * Decreases $instanceTotal's value by 1.  This function should
   * only be called when a clone is removed--existing instances marked
   * for deletion must still be counted toward $instanceTotal's value.
   **/
  function decrementInstanceTotal() {
    var oldInstanceTotalVal = parseInt($instanceTotal.val(), 10),
        newInstanceTotalVal = oldInstanceTotalVal - 1;

    $instanceTotal.val(newInstanceTotalVal);

    return newInstanceTotalVal;
  }

  function toggleRemoveBtns() {
    var activeInstanceTotal = getActiveInstanceTotal(),
        $removeBtns = $form.find('.remove-instance');

    if (activeInstanceTotal === 1) {
      $removeBtns.addClass('hidden');
    }
    else {
      $removeBtns.removeClass('hidden');
    }
  }

  function toggleClonerBtn() {
    var activeInstanceTotal = getActiveInstanceTotal();

    if (activeInstanceTotal < instanceMaxVal) {
      $clonerBtn.removeClass('disabled');
    }
    else {
      $clonerBtn.addClass('disabled');
    }
  }

  function formChangedEventHandler() {
    toggleRemoveBtns();
    toggleClonerBtn();
  }

  /**
   * NOTE: this function should NOT be run until after
   * $instanceTemplate has been defined!
   **/
  function setupInstanceEventHandlers($instance) {
    // Remove any previously assigned click handler
    $instance.off('click', '.remove-instance', removeBtnClickHandler);
    $instance.on('click', '.remove-instance', removeBtnClickHandler);

    // Add event handlers for date/time widgets
    initiateDatePickers($instance.find('.field-date'));
    initiateTimePickers($instance.find('.field-time'));

    // Add event handler for location autocomplete
    eventLocationsSearch($instance.find('.location-dropdown'));

    return $instance;
  }

  function initialFormSetup() {
    // Show the cloner button, add event handler
    $clonerBtn
      .removeClass('hidden')
      .on('click', clonerBtnClickHandler);

    // Apply event handlers to existing instances on page load
    var $instances = $form.find('.event-instance');
    for (var i = 0; i < $instances.length; i++) {
      setupInstanceEventHandlers($instances.eq(i));
    }

    $form
      .on('formChanged', formChangedEventHandler)
      .trigger('formChanged');
  }

  function init() {
    $form = $('#event-instance-form');

    if ($form.length) {
      formPrefix = $form.attr('data-form-prefix');

      instanceTemplateIndex = '__prefix__';
      instanceTemplatePrefix = formPrefix + '-' + instanceTemplateIndex;
      $instanceTemplate = $form.find('#' + instanceTemplatePrefix).detach();

      $clonerBtn = $form.find('#cloner');
      $instanceTotal = $form.siblings('#id_' + formPrefix + '-TOTAL_FORMS');
      instanceMaxVal = parseInt($form.siblings('#id_' + formPrefix + '-MAX_NUM_FORMS').val(), 10);

      initialFormSetup();
    }
  }

  init();
}


/**
 * Sets the event contact information to the current user.
 **/
var eventContactInfo = function() {
    var checkbox = $('#add-user-contact-info');
    // usersFullName and usersEmail are defined in event create/update template
    if (typeof usersFullName !== 'undefined' && typeof usersEmail !== 'undefined') {
        checkbox.on('change', function() {
            var currentName = $('#id_event-contact_name'),
                currentEmail = $('#id_event-contact_email');

            if (usersFullName && usersEmail) {
                if (checkbox.is(':checked')) {
                    currentName.val(usersFullName);
                    currentEmail.val(usersEmail);
                }
                else if (currentName.val() === usersFullName && currentEmail.val() === usersEmail) {
                    currentName.val('');
                    currentEmail.val('');
                }
            }
        });
    }
    else {
        checkbox.parent().hide();
    }
};

var froalaWidget = function() {
    var $editors = $('.froala-widget');

    if ($editors) {
        $editors.editable({
            inlineMode: false,
            buttons: [
                'bold',
                'italic',
                'underline',
                'insertUnorderedList',
                'insertOrderedList',
                'createLink'
            ],
            minHeight: 175
        });
    }
};


$(document).ready(function() {
    bulkSelectAll();
    bulkActionSubmit();
    toggleEventListRecurrences();

    toggleModalMergeObject();
    calendarOwnershipModal();
    toggleModalUserDemote();

    initiateReReviewCopy();

    userSearchTypeahead();
    eventTagging();

    cloneableEventInstances();
    eventContactInfo();
    froalaWidget();
});
