/* Scripts listed below should only need to be executed on the site frontend. */


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
 * Force repaint of map widget on window resize
 **/
var resizeMapWidgets = function() {
    var performResize = function() {
        $('.map-widget').each(function() {
            var widget = $(this),
                widgetWrap = widget.parent('.map-widget-wrap'),
                src = widget.attr('src'),
                regex = /width=\d+\&height=\d+/;

            var newSrc = src.replace(regex, 'width='+widgetWrap.width()+'&height='+widgetWrap.height());
            widget.attr('src', newSrc);
        });
    };

    performResize();

    // on window resize (with timeout to prevent a crapload of Map requests)
    var timeout = false;
    var windowWidth = $(window).width();

    $(window).on('resize', function() {
        if (timeout !== false) {
            clearTimeout(timeout);
        }
        if (windowWidth !== $(window).width()) {
            timeout = setTimeout(performResize, 200);
            windowWidth = $(window).width();
        }
    });
};

/**
 * Used to add styles to the esi data.
 **/
var esiStyle = function() {
    // Style event pages
    if (window.location.pathname.indexOf('event') > -1) {
        $('.event-tag').addClass('label label-default');
    }
};


$(document).ready(function() {
    updateMonthviewDropdown();
    resizeMapWidgets();
    esiStyle();
});
