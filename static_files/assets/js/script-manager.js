/* global eventLocations, usersFullName, usersEmail, EARLIEST_VALID_DATE, LATEST_VALID_DATE, tinyMCE, Bloodhound, TAG_FEED_URL, USERSELECT_URL, CALSELECT_URL, eventPromotedTags */

//
// Import third-party assets
//

// =require bootstrap-3-typeahead/bootstrap3-typeahead.js
// =require timepicker/jquery.timepicker.js
// =require bootstrap-datepicker/dist/js/bootstrap-datepicker.js
// =require select2/dist/js/select2.js


//
// Project-specific scripts
//
// Scripts listed below should only need to be executed on the site backend (manager views.)
//

const typeahead = jQuery.fn.typeahead.noConflict();
jQuery.fn._typeahead = typeahead;

/**
 * Bulk Select for lists of events
 *
 * @return {void}
 **/
const bulkSelectAll = function () {
  $('#bulk-select-all').on('click', function () {
    const selectAll = $(this),
      singleSelects = $('.field-bulk-select input');
    singleSelects.prop('checked', selectAll.is(':checked'));
  });
};


/**
 * Bulk action submit.
 *
 * @return {void}
 **/
const bulkActionSubmit = function () {
  const bulkActionSelects = $('#bulk-action_0, #bulk-action_1');
  bulkActionSelects.removeAttr('onchange');
  $('#bulk-action_0, #bulk-action_1').on('change', function () {
    const bulkForm = this.form;
    const actionInput = $(this);
    const actionInputValue = actionInput.find('option:selected');
    const eventsSelected = $('input:checkbox:checked[name="object_ids"]');
    let recurringEvents = false;

    if (!actionInputValue.attr('value') || actionInputValue.attr('value') === 'empty' || !eventsSelected.length) {
      // Don't do anything if there isn't a value
      return;
    } else if (actionInputValue.val() === 'delete') {
      eventsSelected.each(function () {
        const checkbox = $(this);

        if (parseInt(checkbox.attr('data-event-instance-count'), 10) > 1) {
          recurringEvents = true;
          return false;
        }
      });

      if (recurringEvents) {
        const bulkEventDeleteModal = $('#bulk-event-delete-modal');
        bulkEventDeleteModal.find('#bulk-event-delete-btn').on('click', () => {
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
 * Toggle 'Merge Tag/Category' modal
 *
 * @return {void}
 **/
const toggleModalMergeObject = function () {
  const modal = $('#object-merge-modal');

  $('.category-merge, .tag-merge, .location-merge').on('click', function (e) {
    e.preventDefault();

    const objectTitle = $(this).attr('data-object-title');
    const objectPk    = $(this).attr('data-object-pk');
    const mergeURL    = $(this).attr('href');

    let objectType = '';
    if ($(this).hasClass('category-merge')) {
      objectType = 'category';
    } else {
      objectType = 'tag';
    }

    /* Remove selected object from list of all objects */
    modal
      .find('#new-object-select option')
      .each(function () {
        if ($(this).text() === objectTitle && $(this).val() === objectPk) {
          $(this).prop('disabled', true);
        } else {
          /* Re-enable any previously disabled options from an old modal */
          $(this).prop('disabled', false);
        }
      });

    /* Insert object type/title in modal text */
    modal
      .find('span.object-type')
      .text(objectType)
      .end()
      .find('h2 span.font-weight-normal')
      .text(objectTitle)
      .end()
      .find('.modal-footer a.btn-primary')
      .attr('href', mergeURL)
      .end()
      .modal('show');
  });

  const submitBtn = modal.find('.modal-footer a.btn:first-child');
  submitBtn.on('click', () => {
    const newObject = $('#new-object-select').val();
    let url = submitBtn.attr('href');
    if (newObject !== '') {
      url = url.replace(/merge\/[A-Za-z0-9]+$/, `merge/${newObject}`);
      submitBtn.attr('href', url);
    }
  });
};


/**
 * Update Calendar Ownership Reassignment url value in modal;
 * enable/disable submit button
 *
 * @return {void}
 **/
const calendarOwnershipModal = function () {
  if ($('#calendar-reassign-ownership')) {
    const modal = $('#calendar-reassign-ownership');
    const submitBtn = modal.find('.modal-footer a.btn:first-child');
    submitBtn.on('click', () => {
      const newOwner = $('#new-owner-select').val();
      let url = submitBtn.attr('href');
      if (newOwner !== '') {
        url = url.replace(/user\/[A-Za-z0-9]+$/, `user/${newOwner}`);
        submitBtn.attr('href', url);
      }
    });
  }
};


/**
 * Toggle Calendar user 'demote' modal
 *
 * @return {void}
 **/
const toggleModalUserDemote = function () {
  const modal = $('#user-demote-modal');

  $('.demote-self').on('click', function (e) {
    e.preventDefault();

    const userName  = $(this).attr('data-user-name');
    const demoteURL = $(this).attr('href');

    /* Insert user name in modal text */
    modal
      .find('h2 span.font-weight-normal')
      .text(userName)
      .end()
      .find('.modal-footer a.btn-danger')
      .attr('href', demoteURL)
      .end()
      .modal('show');
  });

  const submitBtn = modal.find('.modal-footer a.btn:first-child');
  submitBtn.on('click', () => {
    const newObject = $('#new-object-select').val();
    let url = submitBtn.attr('href');
    if (newObject !== '') {
      url = url.replace(/merge\/[A-Za-z0-9]+$/, `merge/${newObject}`);
      submitBtn.attr('href', url);
    }
  });
};


/**
 * Defines an onclick event when icons within date/timepickers
 * are clicked.
 *
 * @param {jQuery} icon an icon element.
 * @return {void}
 **/
const fallbackDtpOnClick = function (icon) {
  const input = icon.siblings('input');
  if (!input.is(':focus')) {
    input.focus();
  }
};


/**
 * Datepicker Init.
 * Uses Bootstrap datepicker plugin.
 *
 * @param {jQuery} fields a selection of form fields to initialize against
 * @return {void}
 **/
const initiateDatePickers = function (fields) {
  fields
    .each(function () {
      const field = $(this);

      // Wrap field in wrapper div; add icon
      if (field.parent().hasClass('bootstrap-datepicker') === false) {
        field
          .addClass('form-control')
          .wrap('<div class="bootstrap-dtp bootstrap-datepicker" />')
          .parent()
          .append('<span class="fa fa-calendar" aria-hidden="true" />');
      }

      const fieldParent = field.parent().parent();
      const siblingDateField = fieldParent.siblings().find(`.${field.attr('class')}`);

      field
        .datepicker({
          format: 'mm/dd/yyyy',
          autoclose: true,
          todayHighlight: true,
          startDate: EARLIEST_VALID_DATE,
          endDate: LATEST_VALID_DATE
        })
        .on('changeDate', (e) => {
          // Look for a nearby related start/end date field.  Apply
          // fixed start/end dates to the opposing fields, if possible.
          if (siblingDateField.length && fieldParent.hasClass('start')) {
            siblingDateField.datepicker('setStartDate', e.date);
          } else if (siblingDateField.length && fieldParent.hasClass('end')) {
            siblingDateField.datepicker('setEndDate', e.date);
          }
        });

      // Assign click event to icon
      fieldParent
        .find('span')
        .on('click', function () {
          fallbackDtpOnClick($(this));
        });
    });

};


/**
 * Timepicker init.
 * Uses the jQuery timepicker plugin.
 *
 * @param {jQuery} fields a selection of form fields to initialize against
 * @return {void}
 */
const initiateTimePickers = function (fields) {
  fields
    .each(function () {
      const field = $(this);

      // Wrap each timepicker input if this field isn't a clone
      if (field.parent().hasClass('bootstrap-timepicker') === false) {
        field
          .addClass('form-control')
          .wrap('<div class="bootstrap-dtp bootstrap-timepicker" />')
          .parent()
          .append('<span class="fa fa-clock" aria-hidden="true" />');
      }

      const fieldParent = field.parent().parent();

      // Assign click event to icon
      fieldParent
        .find('span')
        .on('click', function () {
          fallbackDtpOnClick($(this));
        });
    })
    .timepicker({
      scrollDefaultNow: true,
      timeFormat: 'h:i A',
      step: 15
    });
};


/**
 * Adds copied re-review data to their respective fields on the
 * Event Update view.
 *
 * @return {void}
 **/
const initiateReReviewCopy = function () {
  $('#copy_title').on('click', function (e) {
    e.preventDefault();
    $(`#${$(this).attr('data-copy-to')}`).val($('#new_title').val());
  });

  $('#copy_description').on('click', function (e) {
    e.preventDefault();
    tinyMCE.get($(this).attr('data-copy-to')).setContent($('#new_description').val());
  });
};


/**
 * Generic autocomplete class that searches string values from an existing
 * <select> field, or other data, and updates that field as suggestions are
 * found.
 *
 * Methods can be overridden before calling init to customize data parsing.
 *
 * @param {jQuery} autocompleteField jQuery object of the <input> field to
 *     perform autocomplete on
 * @param {jQuery} dataField jQuery object of the <select> field of options
 *     to search against and submit when the form is submitted
 * @return {void}
 **/
const selectFieldAutocomplete = function (autocompleteField, dataField) {
  this.autocompleteField = autocompleteField; // jQuery object of the <input> field to perform autocomplete on
  this.dataField = dataField; // jQuery object of the <select> field of options to search against and submit when the form is submitted.
  this.form = dataField.parents('form'); // The autocomplete <form>
  this.searchableTerms = []; // Array used by Bootstrap typeahead to search queries against. Should contain only strings.
  this.mappedData = {}; // Complete objects that represent searchable data
  this.selection = null; // The current selected autocomplete value

  // Function that performs pre-search setup; i.e. shows/hides various fields.
  this.setupForm = function () {
    return;
  };

  // Prevent form submission via enter keypress in autocomplete field
  this.onFormSubmission = function () {
    const self = this;
    self.form.on('submit', () => {
      if (self.autocompleteField.is(':focus')) {
        return false;
      }
    });
  };

  // Clear hidden field value if autocomplete field is cleared.
  this.checkEmptyValues = function () {
    const self = this;
    self.autocompleteField.on('keydown', (event) => {
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
  this.setSearchTerms = function () {
    const self = this;
    if (self.dataField.is('select')) {
      $.each(self.dataField.children('option:not([disabled])'), function () {
        const option = $(this);
        const key = option.val();
        let val = option.text();
        if ($.trim(val).length < 1) {
          val = `${key} (name n/a)`;
        }

        self.mappedData[val] = key;
        self.searchableTerms.push(val);
      });
    }
  };

  // Function to pass to Bootstrap Typeahead's 'source' method.
  this.typeaheadSource = function (query, process) {
    const self = this;
    return process(self.searchableTerms);
  };

  // Function to pass to Bootstrap Typeahead's 'matcher' method.
  this.typeaheadMatcher = function (item, query) {
    if (item.toLowerCase().indexOf(query.trim().toLowerCase()) !== -1) {
      return true;
    }
  };

  // Function to pass to Bootstrap Typeahead's 'updater' method.
  // This function must return 'item' to keep autocompleteField populated.
  this.typeaheadUpdater = function (item) {
    const self = this;
    self.selection = self.mappedData[item];
    self.dataField.val(self.selection);
    if (self.dataField.is('select')) {
      self.dataField
        .children(`option[value="${self.selection}"]`)
        .attr('selected', true)
        .prop('selected', true);
    }
    return item;
  };

  this.init = function () {
    const self = this;
    self.setupForm();
    self.onFormSubmission();
    self.checkEmptyValues();
    self.setSearchTerms();

    self.autocompleteField.typeahead({
      items: 10,
      minLength: 2,
      source: function (query, process) {
        self.typeaheadSource(query, process);
      },
      matcher: function (item) {
        const query = this.query;
        return self.typeaheadMatcher(item, query);
      },
      updater: function (item) {
        item = self.typeaheadUpdater(item);
        return item;
      }
    });
  };
};


/**
 * User search typeahead + form validation
 *
 * @return {void}
 **/
const userSearchTypeahead = function () {
  $('#id_username_d').select2({
    ajax: {
      url: USERSELECT_URL,
      data: function (params) {
        const query = {
          q: params.term
        };

        return query;
      },
      delay: 250,
      minimumInputLength: 3
    },
    placeholder: 'Search by first name, last name or NID...',
    language: {
      noResults: function () {
        return 'No users found. User must log into the events system at least once to be added to a calendar.';
      }
    }
  });
};


/**
 * Calendar search typeahead + form validation
 *
 * @return {void}
 **/
const calendarSearchTypeahead = function () {
  $('#id_event-calendar').select2({
    ajax: {
      url: CALSELECT_URL,
      data: function (params) {
        const query = {
          q: params.term
        };

        return query;
      },
      delay: 250,
      minimumInputLength: 3,
      placeholder: 'Search by calendar name...'
    }
  });
};

const eventLocationsTypeahead = function (locationDropdowns) {
  if (locationDropdowns.length > 0) {
    const data = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('results'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 10,
      remote: {
        url: `${LOCATION_FEED_URL}?q=%q`,
        wildcard: '%q',
        transform: (response) => {
          return response.results;
        }
      }
    });

    const initializeLocationDropdown = (_idx, obj) => {
      const $locationsField = $(obj).first();
      const $locationRow = $locationsField.parent('.location-search').parent('.row');
      const $locationInput = $locationRow.find('.location-typeahead-input').first();
      const $locationTitleSpan = $locationRow.find('.location-selected-title');
      const $locationRoomSpan = $locationRow.find('.location-selected-room');
      const $locationUrlSpan = $locationRow.find('.location-selected-url');

      const $newLocationBtn = $locationRow.find('.location-typeahead-new-btn');
      const $removeLocationBtn = $locationRow.find('.location-selected-remove');

      const $newLocationForm = $locationRow.find('.location-new-form');
      const $newLocationTitle = $newLocationForm.find('input[name*="-new_location_title"]');

      let hasSelection = false;

      /**
       * Runs when the DOM is ready.
       * @returns {void}
       */
      const onReady = () => {
        if ($locationsField.val() !== '') {
          $removeLocationBtn.show();
        }
      };

      $(onReady);

      /**
       * Click event for the new location button
       * @param {Event} event The event object
       * @returns {void}
       */
      const onNewLocationClick = (event) => {
        event.preventDefault();

        if ($locationsField.val()) {
          $removeLocationBtn.trigger('click');
        }

        const newTitle = $locationInput.val();

        $newLocationTitle.val(newTitle);
        $newLocationForm.show();
        $removeLocationBtn.show();
        $newLocationBtn.hide();

        // Clear out the input val
        $locationInput.typeahead('val', '');
      };

      // Hook up the click event
      $newLocationBtn.on('click', onNewLocationClick);

      /**
       * Click event for the remove location button
       * @param {Event} event The event object
       * @returns {void}
       */
      const onRemoveLocationClick = (event) => {
        event.preventDefault();

        $newLocationForm.hide();
        $locationTitleSpan.hide();
        $locationRoomSpan.hide();
        $locationUrlSpan.hide();

        $removeLocationBtn.hide();

        resetDisplaySpans();
        resetLocationForm();

        $locationsField.val('');
        $locationInput.val('');
      };

      $removeLocationBtn.click(onRemoveLocationClick);

      /**
       * Resets the text on all the location
       * spans for existing locations.
       * @returns {void}
       */
      const resetDisplaySpans = () => {
        $locationTitleSpan.text('');
        $locationRoomSpan.text('');
        $locationUrlSpan.text('');
      };

      /**
       * Resets the new location form
       * @returns {void}
       */
      const resetLocationForm = () => {
        $newLocationForm.find('input').val('');
      };

      /**
       * The select event for the location typeahead.
       * @param {Event} _event Param not used.
       * @param {any} suggestion The suggestion object
       * @returns {void}
       */
      const onSelect = (_event, suggestion) => {
        $locationInput.val('');
        $newLocationBtn.hide();
        $removeLocationBtn.show();

        // Display new values to the user
        if (suggestion.title !== 'None' && suggestion.title !== '') {
          $locationTitleSpan
            .text(suggestion.title)
            .show();
        }

        if (suggestion.room !== 'None' && suggestion.room !== '') {
          $locationRoomSpan
            .text(suggestion.room)
            .show();
        }

        if (suggestion.url !== 'None' && suggestion.url !== '') {
          $locationUrlSpan
            .html(`<a href="${suggestion.url}">${suggestion.url}</a>`)
            .show();
        }

        $locationsField.val(suggestion.id);
      };

      /**
       * Event handler for keydown when the
       * location input is in focus.
       * @param {Event} event The event
       * @returns {bool} Whether the event should continue or not
       */
      const onKeyDown = (event) => {
        const keyCode = event.keyCode || event.which;

        if (event.type === 'keydown' && keyCode === 13 && hasSelection === false) {
          if ($locationInput.val().length < 1) {
            return false;
          }

          $newLocationBtn.trigger('click');
          return false;
        }

        return true;
      };

      /**
       * The event fired whenever the typeahead
       * results are rendered.
       * @returns {void}
       */
      const onRender = () => {
        $newLocationBtn.show();
      };

      const onCursorChanged = (_e, suggestion) => {
        if (suggestion) {
          hasSelection = true;
        } else {
          hasSelection = false;
        }
      };

      $locationInput.typeahead({
        minLength: 3,
        highlight: true
      },
      {
        name: 'location',
        displayKey: 'comboname',
        source: data.ttAdapter()
      }).on('typeahead:select', onSelect)
        .on('typeahead:render', onRender)
        .on('typeahead:cursorchange', onCursorChanged)
        .on('keydown focus', onKeyDown);
    };

    locationDropdowns.each(initializeLocationDropdown);
  }
};

/**
 * Handle the visibility of location content based on the state of the
 * location checkbox. Removes location set values when location type unchecked.
 * param: $('.location-type')
 *
 * @param {jQuery} $locations Location type(s) html elements
 * @return {void}
 **/
const eventLocationTypes = function ($locations) {
  const $submit = $('button[type="submit"]');

  $submit.on('click', () => {
    $locations.each((idx, $obj) => {
      const $locationDiv = $($obj);
      const $locationField = $locationDiv.find('.location-type-field');
      const $locationCheckbox = $locationDiv.find('.location-type-checkbox');
      const $locationContent = $locationDiv.find('.location-type-content');

      // empty set values if $locationCheckbox is unchecked
      if ($locationField.val() !== '' && $locationCheckbox.is(':checked') === false) {

        // empty location values by looking for 'Remove Location' button and triggering if found
        // otherwise set value on field to empty
        const $locationRemoveBtn = $locationContent.find('.location-selected-remove');
        if ($locationRemoveBtn.length !== 0) {
          $locationRemoveBtn.trigger('click');
        } else {
          $locationField.prop('value', '');
        }
      }
    });
  });

  $(() => {
    $locations.each((idx, obj) => {
      const $locationDiv = $(obj);
      const $locationField = $locationDiv.find('.location-type-field');
      const $locationCheckbox = $locationDiv.find('.location-type-checkbox');
      const $locationContent = $locationDiv.find('.location-type-content');

      if ($locationField.val() !== '') {
        $locationCheckbox.prop('checked', true);
        $locationContent.show();
      } else if ($locationField.val() === '' && $locationCheckbox.is(':checked') === false) {
        $locationContent.hide();
      }
    });
  });

  $locations.each((idx, obj) => {
    const $locationDiv = $(obj);
    const $locationCheckbox = $locationDiv.find('.location-type-checkbox');
    const $locationContent = $locationDiv.find('.location-type-content');

    $locationCheckbox.on('click', () => {
      $locationContent.toggle();
    });
  });
};

/**
 * Function tag controls the typeahead logic
 * for the tagging system on the Events Create/Update
 * Views.
 * @author Jim Barnes
 * @since 2.2.0
 * @return {void}
 */
const eventTagging = function () {
  // The field that actually gets submitted
  const $dataField = $('#id_event-tags');
  // The field that appears on screen
  const $inputField = $('#event-tags-typeahead');
  // The button that appears to add new tags
  const $addNewTagBtn = $('#add-new-tag');
  // The parent form
  const $form = $inputField.parents('form');
  // Typeahead object
  let $typeahead = null;

  if (!$dataField.length) {
    return;
  }

  // An array of the currently selected tags
  const selectedTags = [];
  // The unordered list that holds the selected tags
  const $selectedTagList = $('#event-tags-selected');

  /**
   * The initial function that setups the
   * typeahead and on page.
   * @returns {void}
   */
  const setupForm = () => {
    $dataField.hide();
    const val = $dataField.val().trim();
    const tags = !val ? [] : val.split(',');

    $.each(tags, (_idx, tag) => {
      addTagItem({
        id: null,
        text: tag,
        score: 0
      });
    });
  };

  /**
   * On submit handler for the form
   * @param {Event} e The event object
   * @returns {boolean} Returns if the form should submit.
   */
  const onSubmit = (e) => {
    if ($inputField.is(':focus')) {
      e.preventDefault();
      return false;
    }

    return true;
  };

  /**
   * The function that gets called when
   * the window is "ready"
   * @returns {void}
   */
  const onReady = () => {
    setupForm();
    initializeTypeahead();

    $form.on('submit', onSubmit);

    updateTagInput();
  };

  /**
   * Setups everything necessary for the
   * typeahead.
   * @returns {void}
   */
  const initializeTypeahead = () => {
    const data = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('results'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 10,
      remote: {
        url: `${TAG_FEED_URL}?q=%q`,
        wildcard: '%q',
        transform: (response) => {
          return response.results;
        }
      }
    });

    $typeahead = $inputField.typeahead({
      minLength: 3,
      highlight: true
    },
    {
      name: 'tags',
      displayKey: 'text',
      source: data.ttAdapter()
    }).on('typeahead:select', (_event, suggestion) => {
      addTagItem(suggestion);
    }).on('typeahead:render', (_event, suggestions, finished) => {
      if (finished === false) {
        return;
      }

      if (suggestions.length < 1) {
        $addNewTagBtn.show();
      } else {
        $addNewTagBtn.hide();
      }
    }).on('keydown focus', (event) => {
      const keyCode = event.keyCode || event.which;

      if (event.type === 'keydown' && (keyCode === 13 || keyCode === 188)) {
        if ($inputField.val().length < 1) {
          return false;
        }

        $addNewTagBtn.trigger('click');
        return false;
      }

      return true;
    }).on('keyup focus', () => {
      if ($inputField.val().length === 0) {
        $addNewTagBtn.hide();
      }
    });
  };

  /**
   * Handles adding a tag to the selectedTags
   * array as well as the unordered list of tags.
   * @param {any} suggestion The tag objects being added
   * @returns {void}
   */
  const addTagItem = (suggestion) => {
    if (selectedTags.indexOf(suggestion.text) > -1) {
      $inputField.val('');
      return;
    }

    suggestion = cleanSuggestionText(suggestion);

    if (suggestion.promoted) {
      $(`li[data-tag-text="${suggestion.text}"]`).children('a').trigger('click');
      return;
    }

    selectedTags.push(suggestion.text);

    const $removeLink =
      $(`<a href="#" class="selected-remove action-icon" alt="Remove this tag" title="Remove this tag">
          <span class="fa fa-times fa-fw" aria-hidden="true"></span>
          </a>`)
        .on('click', (event) => {
          event.preventDefault();
          removeTagItem(event);
        });

    const $badge =
      $(`<span class="badge badge-pill badge-default mb-2"><span class="tag-name">${suggestion.text}</span></span>`)
        .prepend($removeLink);

    $(`<li class="list-inline-item" data-tag-text="${suggestion.text}"></li>`)
      .prepend($badge)
      .appendTo($selectedTagList);

    if ($typeahead) {
      $typeahead.typeahead('close');
    }

    updateTagInput();
  };

  /**
   * Handles removing the tag object from
   * the selectedTags array and the unordered
   * list of tags.
   * @param {Event} event The initiating click event
   * @returns {void}
   */
  const removeTagItem = (event) => {
    event.preventDefault();
    const $sender = $(event.target);
    const $listItem = $sender.parents('li');
    const dataItem = $listItem.data('tag-text');

    $listItem.remove();

    const tagIndex = selectedTags.indexOf(dataItem);
    if (tagIndex > -1) {
      selectedTags.splice(tagIndex, 1);
    }

    // If the removed tag is a promoted tag, add it back into the Promoted Tags list
    if (eventPromotedTags.indexOf(dataItem) > -1) {
      const $promotedTagList = $('#event-tags-promoted');

      const $tagLink = $(`<a class="promoted-add badge badge-pill badge-success mb-2" href="#" alt="Add this tag" title="Add this tag"><span class="action-icon"><span class="fa fa-plus fa-fw" aria-hidden="true"></span></span><span class="tag-name">${dataItem}</span></a>`);
      $tagLink.on('click', onAddNewPromotedTagBtnClick);
      const $tagLi = $(`<li class="list-inline-item" data-tag-text="${dataItem}"></li>`);
      $tagLink.appendTo($tagLi);
      $tagLi.appendTo($promotedTagList);

      displayPromotedEmptyListMessage();
    }

    updateTagInput();
  };

  /**
   * Helper function that updates the
   * dataField, inputField and hides the
   * new Tag button.
   * @returns {void}
   */
  const updateTagInput = () => {
    let value = selectedTags.join(',');
    if (!value.indexOf(',', value.length - 1) !== -1 && value !== '') {
      value += ',';
    }

    $dataField.val(value);
    $inputField.val('');
    $addNewTagBtn.hide();
  };

  /**
   * The logic for when the add new tag button
   * is clicked.
   * @param {Event} e The click event object
   * @returns {void}
   */
  const onAddNewTagBtnClick = (e) => {
    e.preventDefault();

    // Get the text that's typed in and trim.
    const newTag = $inputField.val().trim();

    addTagItem({
      id: null,
      text: newTag,
      score: 0
    });
  };

  /**
   * Cleans the text of the suggestion object
   * by passing it through a result expression
   * that only allows whitelisted characters.
   * @param {any} suggestion The suggestion object
   * @returns {any} The suggestion object
   */
  const cleanSuggestionText = (suggestion) => {
    suggestion.text = $.trim(suggestion.text.replace(/([^a-zA-Z0-9\s-!$#%&+|:?'])/g, ''));
    return suggestion;
  };

  /**
   * Hides promoted tags that are already in the
   * selected tags list.
   *
   * @returns {void}
   */
  const cleanPromotedTagList = () => {
    // Get and clean existing tags
    const dataFieldVal = $dataField.val().trim();
    const existingTags = !dataFieldVal ? [] : dataFieldVal.split(',');

    for (let i = 0; i < existingTags.length; i++) {
      // Uses the same expression as cleanSuggestionText
      existingTags[i] = $.trim(existingTags[i].replace(/([^a-zA-Z0-9\s-!$#%&+|:?'])/g, ''));
    }

    $('.promoted-add').each((idx, obj) => {
      const $promotedTag = $(obj);
      const promotedTagText = $promotedTag.children('.tag-name').text();

      if ($.inArray(promotedTagText, existingTags) !== -1) {
        $promotedTag.parent().remove();
      }
    });

    displayPromotedEmptyListMessage();
  };

  /**
   * The logic for when the add new promoted tag
   * button is clicked.
   * @param {Event} e The click event object
   * @returns {void}
   */
  const onAddNewPromotedTagBtnClick = (e) => {
    e.preventDefault();

    const $promotedTagBtn = $(e.target).closest('.promoted-add');
    const $promotedTagText = $promotedTagBtn.text();

    addTagItem({
      id: null,
      text: $promotedTagText,
      score: 0
    });

    $promotedTagBtn.parents('li').remove();

    displayPromotedEmptyListMessage();
  };

  // Displays an empty promoted tag list message
  // if promoted list is empty
  const displayPromotedEmptyListMessage = () => {
    if ($('#event-tags-promoted li').length <= 0) {
      $('.empty-promoted-tags').removeClass('d-none');
    } else {
      $('.empty-promoted-tags').addClass('d-none');
    }
  };

  $(onReady);
  $addNewTagBtn.on('click', onAddNewTagBtnClick);

  cleanPromotedTagList();
  $('.promoted-add').on('click', onAddNewPromotedTagBtnClick);
};


/**
 * Handle the visibility of the registration fields based on the
 * state of the registration checkbox.
 *
 * @return {void}
 **/
const eventRegistrationFields = function () {
  const checkbox = $('#id_event-registration_checkbox');
  const registrationFieldsContainer = $('#event-registration-fields');
  const registrationLinkField = $('#id_event-registration_link');
  const registrationInfoField = $('#id_event-registration_info');

  // Check checkbox and show registrationFieldsContainer if registrationLinkField is not empty
  if (registrationLinkField.val() || registrationFieldsContainer.hasClass('error')) {
    checkbox.prop('checked', true);
    registrationFieldsContainer.show();
  }

  checkbox.on('change', () => {
    registrationFieldsContainer.slideToggle(300);
  });

  // Clear out registration fields values upon form submission if checkbox is unchecked
  const $submit = $('button[type="submit"]');
  $submit.on('click', () => {
    if (registrationLinkField.val() !== '' && checkbox.is(':checked') === false) {
      registrationLinkField.prop('value', '');
      registrationInfoField.prop('value', '');
    }
  });
};


/**
 * Clone fieldsets of the EventInstance formset of the Event Create/Update form.
 * Auto-increment field IDs as necessary.
 *
 * @return {void}
 **/
function cloneableEventInstances() {
  let $clonerBtn, // Not technically a form, but the <fieldset> that wraps the event instance forms
    $form, // Serves as a base for generating new event instance form prefixes
    $instanceTemplate, // Reference to clean markup from which event instance form clones should be created
    $instanceTotal, // Some arbitrary string; gets appended to instanceTemplatePrefix
    formPrefix, // Prefix for form field and input IDs, labels, and other attributes for $instanceTemplate
    instanceMaxVal, // Button that generates new clones when clicked
    instanceTemplateIndex, // Hidden input used by Django which stores the total number of instances in $form (that aren't deleted)
    instanceTemplatePrefix; // Grabbed from hidden input used by Django; the max number of instances that can be saved to an event

  /**
   * Updates IDs, labels, etc. as necessary for Event Instance formsets.
   * This function checks for form elements specific to Event Instances
   * (checkboxes, inputs, selects)--if new form elements are ever added to
   * the Event Instance formset, this function may need to be updated.
   *
   * @param {jQuery} $instance an element containing an Event Instance formset
   * @param {str} oldPrefix an old prefix to replace in formset element attrs
   * @param {str} newPrefix a new prefix to inject into formset element attrs
   * @return {jQuery}
   **/
  function updateInstancePrefix($instance, oldPrefix, newPrefix) {

    // Update $instance's ID
    $instance.attr('id', newPrefix);

    const $prefixedElements = $instance.find('checkbox, input, select, label');
    const $removeBtn = $instance.find('.remove-instance');
    const regex = new RegExp(oldPrefix, 'gm');

    for (let i = 0; i < $prefixedElements.length; i++) {
      const $elem = $prefixedElements.eq(i);
      const attrFor = $elem.attr('for');
      const attrID = $elem.attr('id');
      const attrName = $elem.attr('name');

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

    $removeBtn.attr('data-instance', `#${newPrefix}`);

    return $instance;
  }

  /**
   * Clone $instanceTemplate and insert at the bottom of the
   * Event Instance form
   *
   * @return {void}
   **/
  function addInstance() {
    const activeInstanceTotal = getActiveInstanceTotal();
    if (activeInstanceTotal < instanceMaxVal) {
      let $instance = $instanceTemplate.clone(false);
      const $instances = $form.find('.event-instance');
      const newPrefix = `${formPrefix}-${$instances.length}`;

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
    } else {
      window.alert(`Sorry, an event cannot have more than ${instanceMaxVal} unique event instances.`);
    }
  }

  function clonerBtnClickHandler(e) {
    e.preventDefault();
    addInstance();
  }

  /**
   * Callback after an event instance is "removed"
   *
   * @return {void}
   **/
  function updateInstancesPostRemoval() {

    const $removedInstance = $(this); // passed from slideUp() callback

    // If this instance was never saved to the backend (is a clone),
    // remove it from the DOM entirely.  Else, keep it in the DOM but
    // check the DELETE checkbox for the instance
    if ($removedInstance.hasClass('clone')) {
      $removedInstance.remove();

      const $instances = $form.find('.event-instance');

      // Go through all instances and update prefixes on clones, since
      // they may be out of order now
      for (let index = 0; index < $instances.length; index++) {
        const $theInstance = $instances.eq(index);

        // Only modify prefixes of clones (non-clones should never fall out of order)
        if ($theInstance.hasClass('clone')) {
          const newPrefix = `${formPrefix}-${index}`;
          updateInstancePrefix($theInstance, $theInstance.attr('id'), newPrefix);
          setupInstanceEventHandlers($theInstance);
        }
      }
    } else {
      $removedInstance
        .addClass('event-instance-removed')
        .find(`#id_${$removedInstance.attr('id')}-DELETE`)
        .prop('checked', true);
    }

    $form.trigger('formChanged');
  }

  /**
   * Hide the given Event Instance and mark it for removal
   * on form submit.  Update remaining Event Instance prefixes.
   *
   * @param {jQuery} $instance an element surrounding an Event Instance formset
   * @return {void}
   **/
  function removeInstance($instance) {
    const activeInstanceTotal = getActiveInstanceTotal(),
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
    const $btn = $(e.target);
    removeInstance($form.find($btn.attr('data-instance')));
  }

  /**
   * Returns the number of .event-instance's in the form that are not marked
   * for deletion (instances that are "actively" visible).
   *
   * @return {void}
   **/
  function getActiveInstanceTotal() {
    return $form.find('.event-instance:not(.event-instance-removed)').length;
  }

  /**
   * Increments $instanceTotal's value by 1.  This function should always
   * be called any time an instance is added to $form.
   *
   * @return {int}
   **/
  function incrementInstanceTotal() {
    const oldInstanceTotalVal = parseInt($instanceTotal.val(), 10);
    const newInstanceTotalVal = oldInstanceTotalVal + 1;

    $instanceTotal.val(newInstanceTotalVal);

    return newInstanceTotalVal;
  }

  /**
   * Decreases $instanceTotal's value by 1.  This function should
   * only be called when a clone is removed--existing instances marked
   * for deletion must still be counted toward $instanceTotal's value.
   *
   * @return {int}
   **/
  function decrementInstanceTotal() {
    const oldInstanceTotalVal = parseInt($instanceTotal.val(), 10);
    const newInstanceTotalVal = oldInstanceTotalVal - 1;

    $instanceTotal.val(newInstanceTotalVal);

    return newInstanceTotalVal;
  }

  function toggleRemoveBtns() {
    const activeInstanceTotal = getActiveInstanceTotal();
    const $removeBtns = $form.find('.remove-instance');

    if (activeInstanceTotal === 1) {
      $removeBtns.addClass('d-none');
    } else {
      $removeBtns.removeClass('d-none');
    }
  }

  function toggleClonerBtn() {
    const activeInstanceTotal = getActiveInstanceTotal();

    if (activeInstanceTotal < instanceMaxVal) {
      $clonerBtn.removeClass('disabled');
    } else {
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
   *
   * @param {jQuery} $instance an element containing an Event Instance formset
   * @return {jQuery}
   **/
  function setupInstanceEventHandlers($instance) {
    // Remove any previously assigned click handler
    $instance.off('click', '.remove-instance', removeBtnClickHandler);
    $instance.on('click', '.remove-instance', removeBtnClickHandler);

    // Add event handlers for date/time widgets
    initiateDatePickers($instance.find('.field-date'));
    initiateTimePickers($instance.find('.field-time'));

    // Add event handler for location autocomplete
    eventLocationsTypeahead($instance.find('.location-dropdown'));

    // Add event handler for location type visibility
    eventLocationTypes($instance.find('.location-type'));

    return $instance;
  }

  function initialFormSetup() {
    // Show the cloner button, add event handler
    $clonerBtn
      .removeClass('d-none')
      .on('click', clonerBtnClickHandler);

    // Apply event handlers to existing instances on page load
    const $instances = $form.find('.event-instance');
    for (let i = 0; i < $instances.length; i++) {
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
      instanceTemplatePrefix = `${formPrefix}-${instanceTemplateIndex}`;
      $instanceTemplate = $form.find(`#${instanceTemplatePrefix}`).detach();

      $clonerBtn = $form.find('#cloner');
      $instanceTotal = $form.siblings(`#id_${formPrefix}-TOTAL_FORMS`);
      instanceMaxVal = parseInt($form.siblings(`#id_${formPrefix}-MAX_NUM_FORMS`).val(), 10);

      initialFormSetup();
    }
  }

  init();
}


/**
 * Sets the event contact information to the current user.
 *
 * @return {void}
 **/
const eventContactInfo = function () {
  const checkbox = $('#add-user-contact-info');
  // usersFullName and usersEmail are defined in event create/update template
  if (typeof usersFullName !== 'undefined' && typeof usersEmail !== 'undefined') {
    checkbox.on('change', () => {
      const currentName = $('#id_event-contact_name');
      const currentEmail = $('#id_event-contact_email');

      if (usersFullName && usersEmail) {
        if (checkbox.is(':checked')) {
          currentName.val(usersFullName);
          currentEmail.val(usersEmail);
        } else if (currentName.val() === usersFullName && currentEmail.val() === usersEmail) {
          currentName.val('');
          currentEmail.val('');
        }
      }
    });
  } else {
    checkbox.parent().hide();
  }
};


const initiateWysiwygs = function () {
  /* eslint-disable camelcase */
  const $editors = $('.wysiwyg');

  if ($editors.length) {
    tinyMCE.init({
      selector: '.wysiwyg',
      browser_spellcheck: true,
      plugins: 'link paste autoresize lists',
      // valid elems/styles configuration below should match with
      // BLEACH_ALLOWED_[] settings in settings_local.py
      valid_elements: 'p[style],span[style],br,strong/b,em/i,u,a[href|title|style|alt|target=_blank],ul,ol,li',
      valid_styles: {
        p: 'font-weight,text-decoration',
        span: 'font-weight,text-decoration',
        a: 'font-weight,text-decoration'
      },
      statusbar: false,
      menubar: false,
      toolbar: 'bold italic underline | bullist numlist | link',
      autoresize_bottom_margin: 10,
      min_height: 400,
      theme: 'silver'
    });
  }
  /* eslint-enable camelcase */
};


$(() => {
  bulkSelectAll();
  bulkActionSubmit();

  toggleModalMergeObject();
  calendarOwnershipModal();
  toggleModalUserDemote();

  initiateReReviewCopy();

  userSearchTypeahead();
  calendarSearchTypeahead();
  eventTagging();

  eventRegistrationFields();
  cloneableEventInstances();
  eventContactInfo();
  initiateWysiwygs();
});
