/* global ga */

/* Scripts listed below should be view-agnostic (can run in frontend or backend.) */


/**
 * Assign browser-specific body classes on page load
 **/
var addBodyClasses = function() {
    var bodyClass = '';
    // Old IE:
    if (/MSIE (\d+\.\d+);/.test(navigator.userAgent)) { //test for MSIE x.x;
        var ieversion = Number(RegExp.$1); // capture x.x portion and store as a number
        if (ieversion >= 10) { bodyClass = 'ie ie10'; }
        else if (ieversion >= 9) { bodyClass = 'ie ie9'; }
        else if (ieversion >= 8) { bodyClass = 'ie ie8'; }
        else if (ieversion >= 7) { bodyClass = 'ie ie7'; }
    }
    // IE11+:
    else if (navigator.appName === 'Netscape' && !!navigator.userAgent.match(/Trident\/7.0/)) { bodyClass = 'ie ie11'; }
    // iOS:
    else if (navigator.userAgent.match(/iPhone/i)) { bodyClass = 'iphone'; }
    else if (navigator.userAgent.match(/iPad/i)) { bodyClass = 'ipad'; }
    else if (navigator.userAgent.match(/iPod/i)) { bodyClass = 'ipod'; }
    // Android:
    else if (navigator.userAgent.match(/Android/i)) { bodyClass = 'android'; }

    $('body').addClass(bodyClass);
};


/**
 * Add classes to elements in IE8 that require non-supported CSS selectors for styling
 **/
var ie8StyleClasses = function() {
    var addClassBySelector = function(selector, classToAdd) {
        $(selector).each(function() { $(this).addClass(classToAdd); });
    };
    if ($('body').hasClass('ie8')) {
        // a:not('.btn') > i; i + a:not('.btn')
        addClassBySelector('a:not(.btn) > i', 'icon-right-margin');
        addClassBySelector('i + a:not(.btn)', 'icon-left-margin');
        // general :last-child usage
        addClassBySelector('.edit-options > ul > li:last-child', 'last-child');
        addClassBySelector('.search-results-list > li:last-child', 'last-child');
        addClassBySelector('.search-results-list .event-tags ul li:last-child', 'last-child');
        addClassBySelector('.panel-heading .form-group:last-child, .panel-footer .form-group:last-child', 'last-child');
    }
};


/**
 * Attempt to remove scrollbars on dropdown menus if they don't scroll vertically
 **/
var hideDropdownScrollbars = function() {
    $('.dropdown').each(function() {
        $(this).on('shown.bs.dropdown', function() {
            var dropdownMenu = $(this).find('.dropdown-menu');
            if (dropdownMenu.outerHeight() >= dropdownMenu.prop('scrollHeight')) {
                dropdownMenu.css('overflow-y', 'hidden');
            }
            else {
                dropdownMenu.css('overflow-y', 'scroll');
            }
        });
    });
};


/**
 * Replace browser's default hover effect for <abbr> elements with Bootstrap tooltips,
 * due to wide browser inconsistency on how the hover state works
 **/
var abbrTooltips = function() {
    $('abbr').each(function() { $(this).tooltip(); } );
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
 * Jump to an anchor on the page with smooth scrolling and highlight it
 **/
var jumpTo = function() {
    $('.jump-to').on('click', function() {
        var id = $(this).attr('href');
        var elem = $(id);
        var useGlow = $(this).hasClass('jump-to-glow');

        if (useGlow) {
            elem
                .removeClass('jump-to-target jump-to-target-active')
                .addClass('jump-to-target jump-to-target-active');
        }

        $('html,body').animate({
            scrollTop: elem.offset().top
        }, 300);

        if (useGlow) {
            setTimeout(function() {
                elem.removeClass('jump-to-target jump-to-target-active');
            }, 4000);
        }

        return false;
    });
};


/**
 * Toggle Generic Object modification/deletion modal.
 *
 * Populates modal contents with the static form specified
 * in the toggle link's 'href' attribute.
 **/
var toggleModalModifyObject = function() {
    $('.object-modify').on('click', function(e) {
        e.preventDefault();

        var modifyBtn = $(this),
            staticPgUrl = modifyBtn.attr('href'),
            modal = $('#object-modify-modal');

        if (modal) {
            $.ajax({
                url: staticPgUrl,
                timeout: 3000 // allow 3 seconds to pass before failing the ajax request
            })
                .done(function(html) {
                    // Assign returned html to some element so we can traverse the dom successfully
                    var markup = $('<div />');
                    markup.html(html);

                    var modalTitle = '',
                        modalBody = '',
                        modalFooter = '',
                        formId = '';

                    // Grab data from the requested page. Check it to make sure it's not
                    // an error message or something we don't want
                    if (markup.find('.object-modify-form').length > 0) {
                        modalTitle = markup.find('h1').html();
                        modalBody = markup.find('.modal-body-content').html();
                        modalFooter = markup.find('.modal-footer-content').html();
                        formId = markup.find('.object-modify-form').attr('id');
                    }
                    else {
                        modalTitle = 'Error';
                        modalBody = '<p>You do not have access to this content.</p>';
                        modalFooter = '<a class="btn" data-dismiss="modal" href="#">Close</a>';
                        formId = 'object-modify';
                    }

                    modal
                        .find('h2')
                            .html(modalTitle)
                            .end()
                        .find('form')
                            .attr('action', staticPgUrl)
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
                .fail(function() {
                    // Just redirect to the static modify/delete page for the object
                    window.location = staticPgUrl;
                });
        }
        else { window.location = staticPgUrl; }
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
 * Add support for forms within Bootstrap .dropdown-menus.
 **/
var dropdownMenuForms = function() {
    $('.dropdown-menu').on('click', function(e) {
        if ($(this).hasClass('dropdown-menu-form')) {
            e.stopPropagation();
        }
    });
};


/**
 * Add ability to make an entire table row a clickable link out,
 * based on a provided link in the row.
 **/
var clickableTableRows = function() {
    $('.table-clickable tr')
        .css('cursor', 'pointer')
        .on('click', function() {
            var link = $(this).find('a.row-link:first-child').attr('href');
            if (link) {
                window.location.href = link;
                return true;
            }
            else { return false; }
        });
};


/**
 * Functionality for content expanders (i.e. event descriptions)
 **/
var contentExpanders = function() {
    $('.content-expander').each(function() {
        var btn = $(this),
            content = btn.parents('.content-expand');

        // Hide btn if content is less than max-height
        if (content.height() < parseInt(content.css('max-height'), 10)) {
            btn.addClass('hidden');
        }

        btn.on('click', function(e) {
            e.preventDefault();
            content.addClass('expanded');
        });
    });
};


/**
 * Remove .dropdown-menu-right class from .edit-options list items @ mobile size
 **/
var mobileEditOptions = function() {
    var removeClass = function() {
        if ($(window).width() < 768) {
            $('#page-title-wrap .edit-options .dropdown-menu-right').removeClass('dropdown-menu-right');
        }
    };

    removeClass();
    $(window).on('resize', function() { removeClass(); });
};


/**
 * Google Analytics click event tracking
 *
 * interaction: default 'event'. Used to distinguish unique interactions, i.e. social interactions
 * category: the interaction category; for social interactions, this is the 'socialNetwork' value
 * action: the name of the object and the action taken, e.g. 'Contact Email click' or 'like' for social ('socialAction' value)
 * label: the page the user is leaving; for social, this is the 'socialTarget' value
 **/
var gaEventTracking = function() {
    $('.ga-event').on('click', function(e) {
        e.preventDefault();

        var link = $(this),
            url = link.attr('href'),
            interaction = link.attr('data-ga-interaction') ? link.attr('data-ga-interaction') : 'event',
            category = link.attr('data-ga-category') ? link.attr('data-ga-category') : 'Outbound Links',
            action = link.attr('data-ga-action'),
            label = link.attr('data-ga-label');

        if (typeof ga !== 'undefined' && action !== null && label !== null) {
            ga('send', interaction, category, action, label);
            window.setTimeout(function(){ document.location = url; }, 200);
        }
        else {
            document.location = url;
        }
    });
};


$(document).ready(function() {
    $('input, textarea').placeholder();
    
    addBodyClasses();
    ie8StyleClasses();
    hideDropdownScrollbars();
    abbrTooltips();
    autoOpenTagByAnchor();
    jumpTo();
    toggleModalModifyObject();
    calendarSliders();
    dropdownMenuForms();
    clickableTableRows();
    contentExpanders();
    mobileEditOptions();
    gaEventTracking();
});
