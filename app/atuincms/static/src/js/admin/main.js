$(function () {
	/*
	 * Template:
	 *
	 * $('html.example_section').each(function () {
	 * 	// call initialization function
	 * 	init_example_section()
	 * });
	 */

	$('html.admin.cms.menus').each(function () {
		bindMenusAdmin();
	});
	$('html.admin.cms.sections').each(function () {
		bindSectionsAdmin();
	});
	$('html.admin.cms.pageNew').each(function () {
		bindPageNewAdmin();
	});
	$('html.admin.cms.page').each(function () {
		bindPageAdmin();
		bindMediaTextsAdmin();
		bindMediaImagesAdmin();
		bindMediaLinkedPagesAdmin();
		bindMediaLinkedSectionsAdmin();
	});
});