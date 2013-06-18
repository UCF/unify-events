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
 * TinyMCE Init
 **/
tinymce.init({
    selector: "textarea",
    plugins: [
        "advlist autolink lists link image charmap print preview anchor",
         "searchreplace visualblocks code fullscreen",
         "insertdatetime media table contextmenu paste moxiemanager"
    ],
    toolbar: "insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image"
});
