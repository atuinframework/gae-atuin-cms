$(function () {
	/*
	 * Template:
	 *
	 * $('html.example_section').each(function () {
	 * 	// call initialization function
	 * 	init_example_section()
	 * });
	 */

	$('html.cms.page.realization').each(function () {
		bindRealizationAdmin();
	});
});