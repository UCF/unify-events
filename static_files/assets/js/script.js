/* global ga */

//
// Import third-party assets
//

// =require jquery-placeholder/jquery.placeholder.js

// Athena
// =require ucf-athena-framework/dist/js/framework.min.js


//
// Project-specific scripts
//
// Scripts listed below should be view-agnostic (can run in frontend or backend.)
//


// TODO: Where is this used and does it work?
/**
 * Jump to an anchor on the page with smooth scrolling and highlight it
 *
 * @return {void}
 **/
const jumpTo = function () {
  $('.jump-to').on('click', function () {
    const id = $(this).attr('href');
    const elem = $(id);
    const useGlow = $(this).hasClass('jump-to-glow');
    const adminBar = $('.nav-wrap');
    let pageTopPadding = 20; // some default padding btwn top of pg and content

    if (adminBar.length) {
      pageTopPadding += adminBar.height();
    }

    if (useGlow) {
      elem
        .removeClass('jump-to-target jump-to-target-active')
        .addClass('jump-to-target jump-to-target-active');
    }

    $('html,body').animate({
      scrollTop: elem.offset().top - pageTopPadding
    }, 300);

    if (useGlow) {
      setTimeout(() => {
        elem.removeClass('jump-to-target jump-to-target-active');
      }, 4000);
    }

    return false;
  });
};


// TODO: Review this and make sure classes, everything looks good
/**
 * Toggle Generic Object modification/deletion modal.
 *
 * Populates modal contents with the static form specified
 * in the toggle link's 'href' attribute.
 *
 * @return {void}
 **/
const toggleModalModifyObject = function () {
  $('.object-modify').on('click', function (e) {
    e.preventDefault();

    const $modifyBtn  = $(this);
    const staticPgUrl = $modifyBtn.attr('href');
    const $modal      = $('#object-modify-modal');

    if ($modal) {
      $.ajax({
        url: staticPgUrl,
        timeout: 3000 // allow 3 seconds to pass before failing the ajax request
      })
        .done((html) => {
          // Assign returned html to some element so we can traverse the dom successfully
          const $markup = $('<div />');
          $markup.html(html);

          const $form = $markup.find('.object-modify-form');
          let modalTitle = '';
          let modalBody = '';
          let modalFooter = '';
          let formAction = staticPgUrl;
          let formId = '';

          // Grab data from the requested page. Check it to make sure it's not
          // an error message or something we don't want
          if ($form.length) {
            modalTitle = $markup.find('h1').html();
            modalBody = $markup.find('.modal-body-content').html();
            modalFooter = $markup.find('.modal-footer-content').html();
            formAction = $form.attr('action') || formAction;
            formId = $form.attr('id');
          } else {
            modalTitle = 'Error';
            modalBody = '<p>You do not have access to this content.</p>';
            modalFooter = '<a class="btn" data-dismiss="modal" href="#">Close</a>';
            formId = 'object-modify';
          }

          $modal
            .find('h2')
            .html(modalTitle)
            .end()
            .find('form')
            .attr('action', formAction)
            .attr('id', formId)
            .end()
            .find('.modal-body')
            .html(modalBody)
            .end()
            .find('.modal-footer')
            .html(modalFooter)
            .end()
            .modal('show');
        })
        .fail(() => {
          // Just redirect to the static modify/delete page for the object
          window.location = staticPgUrl;
        });
    } else {
      window.location = staticPgUrl;
    }
  });
};


/**
 * Calendar grid sliders
 *
 * @return {void}
 **/
const calendarSliders = function () {
  $('body').on('click', '.calendar-slider ul.pager li a', function (e) {
    e.preventDefault();

    const slider = $(this).parents('.calendar-slider');
    $.get($(this).attr('data-ajax-link'), (data) => {
      slider.replaceWith(data);
    });
  });
};


// TODO: Do we need this?
/**
 * Add support for forms within Bootstrap .dropdown-menus.
 *
 * @return {void}
 **/
const dropdownMenuForms = function () {
  $('.dropdown-menu').on('click', function (e) {
    if ($(this).hasClass('dropdown-menu-form')) {
      e.stopPropagation();
    }
  });
};


// TODO: Is this needed?
/**
 * Add ability to make an entire table row a clickable link out,
 * based on a provided link in the row.
 *
 * @return {void}
 **/
const clickableTableRows = function () {
  $('.table-clickable tr')
    .css('cursor', 'pointer')
    .on('click', function () {
      const link = $(this).find('a.row-link:first-child').attr('href');
      if (link) {
        window.location.href = link;
        return true;
      }
      return false;
    });
};


// TODO: Review this functionality
/**
 * Functionality for content expanders (i.e. event descriptions)
 *
 * @return {void}
 **/
const contentExpanders = function () {
  $('.content-expander').each(function () {
    const btn = $(this),
      content = btn.parents('.content-expand');

    // Hide btn if content is less than max-height
    if (content.height() < parseInt(content.css('max-height'), 10)) {
      // TODO: Change this to d-none?
      btn.addClass('hidden');
    }

    btn.on('click', (e) => {
      e.preventDefault();
      content.addClass('expanded');
    });
  });
};


/**
 * Google Analytics click event tracking
 *
 * interaction: default 'event'. Used to distinguish unique interactions, i.e. social interactions
 * category: the interaction category; for social interactions, this is the 'socialNetwork' value
 * action: the name of the object and the action taken, e.g. 'Contact Email click' or 'like' for social ('socialAction' value)
 * label: the page the user is leaving; for social, this is the 'socialTarget' value
 *
 * @return {void}
 **/
const gaEventTracking = function () {
  $('.ga-event').on('click', function (e) {
    e.preventDefault();

    const link = $(this);
    const url = link.attr('href');
    const target = link.attr('target');
    const interaction = link.attr('data-ga-interaction') ? link.attr('data-ga-interaction') : 'event';
    const category = link.attr('data-ga-category') ? link.attr('data-ga-category') : 'Outbound Links';
    const action = link.attr('data-ga-action');
    const label = link.attr('data-ga-label');

    const windowLocation = function (url, target) {
      if (target === '_blank') {
        window.open(url, '_blank');
      } else {
        document.location = url;
      }
    };

    if (typeof ga !== 'undefined' && action !== null && label !== null) {
      ga('send', interaction, category, action, label);
      window.setTimeout(() => {
        windowLocation(url, target);
      }, 200);
    } else {
      windowLocation(url, target);
    }
  });
};


/**
 * Enable Athena tooltips
 *
 * @return {void}
 **/
const enableTooltips = function () {
  $('[data-toggle="tooltip"]').tooltip();
};


$(() => {
  $('input, textarea').placeholder();

  jumpTo();
  toggleModalModifyObject();
  calendarSliders();
  dropdownMenuForms();
  clickableTableRows();
  contentExpanders();
  gaEventTracking();
  enableTooltips();
});
