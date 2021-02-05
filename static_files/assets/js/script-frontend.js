/* Scripts listed below should only need to be executed on the site frontend. */


/**
 * Update frontend calendar month view month/year form
 * "action" value on dropdown change
 *
 * @return {void}
 **/
const updateMonthViewDropdown = function () {
  const form = $('#month-toggle');
  const yearSelect = form.find('#id_year');
  const monthSelect = form.find('#id_month');

  monthSelect.on('change', function () {
    const action = form.attr('action');
    const newMonth = `/${$(this).val()}/`;
    const oldMonth = action.slice(action.length - 4, action.length);
    const newAction = action.replace(oldMonth, newMonth);
    form.attr('action', newAction);
  });

  yearSelect.on('change', function () {
    const action = form.attr('action');
    const newYear = `/${$(this).val()}/`;
    const oldYear = action.slice(action.length - 9, action.length - 3);
    const newAction = action.replace(oldYear, newYear);
    form.attr('action', newAction);
  });
};


/**
 * Force repaint of map widget on window resize
 *
 * @return {void}
 **/
const resizeMapWidgets = function () {
  const performResize = function () {
    $('.map-widget').each(function () {
      const widget = $(this);
      const widgetWrap = widget.parent('.map-widget-wrap');
      const src = widget.attr('src');
      const regex = /width=\d+&height=\d+/;

      const newSrc = src.replace(regex, `width=${widgetWrap.width()}&height=${widgetWrap.height()}`);
      widget.attr('src', newSrc);
    });
  };

  performResize();

  // on window resize (with timeout to prevent a crapload of Map requests)
  let timeout = false;
  let windowWidth = $(window).width();

  $(window).on('resize', () => {
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
 *
 * @return {void}
 **/
const esiStyle = function () {
  // Style event pages
  if (window.location.pathname.indexOf('event') > -1) {
    $('.event-tag').addClass('tag-cloud-link');
  }
};


$(() => {
  updateMonthViewDropdown();
  resizeMapWidgets();
  esiStyle();
});
